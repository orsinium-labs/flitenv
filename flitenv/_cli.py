import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

import toml

from ._constants import MAIN_ENV
from ._deps_manager import DepsManager
from ._venv import VEnv


def cmd_lock(deps: DepsManager, args) -> int:
    return deps.lock(constraint=args.constraint)


def cmd_install(deps: DepsManager, args) -> int:
    return deps.install()


def cmd_run(deps: DepsManager, args) -> int:
    return deps.run(args.exe, *args.args)


def cmd_version(deps: DepsManager, args) -> int:
    from . import __version__
    print(__version__, file=deps.stream)
    return 0


def get_envs() -> typing.Optional[typing.List[str]]:
    path = Path('pyproject.toml')
    if not path.exists():
        return None
    with path.open('r', encoding='utf-8') as stream:
        pyproject = toml.load(stream)
    try:
        meta = pyproject['tool']['flit']['metadata']
    except KeyError:
        return None
    try:
        envs = meta['requires-extra']
    except KeyError:
        return [MAIN_ENV]
    return [MAIN_ENV] + sorted(envs)


def main(argv: typing.List[str], stream: typing.TextIO) -> int:

    parser = ArgumentParser()
    parser.format_help
    parser.add_argument('env', choices=get_envs())  # type: ignore
    parser.add_argument('--root', type=Path, default=Path())
    parser.add_argument('--venvs', type=Path)
    subparsers = parser.add_subparsers(dest='cmd')

    lock_parser = subparsers.add_parser(
        name='lock',
        help='lock env dependencies',
    )
    lock_parser.add_argument('-c', '--constraint')
    lock_parser.set_defaults(func=cmd_lock)

    install_parser = subparsers.add_parser(
        name='install',
        help='install env dependencies',
    )
    install_parser.set_defaults(func=cmd_install)

    run_parser = subparsers.add_parser(
        name='run',
        help='run a command inside the env',
    )
    run_parser.add_argument('exe')
    run_parser.add_argument('args', nargs='...')
    run_parser.set_defaults(func=cmd_run)

    version_parser = subparsers.add_parser(
        name='version',
        help='print flitenv version and exit',
    )
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args(argv)
    if args.cmd is None:
        print('command required', file=stream)
        return 1
    venv = VEnv(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
    )
    deps = DepsManager(
        root=args.root,
        venv=venv,
        stream=stream,
    )
    return args.func(deps=deps, args=args)


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stream=sys.stdout))
