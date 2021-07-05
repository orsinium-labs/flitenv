import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

import toml

from ._core import Env, MAIN_ENV


def cmd_lock(env: Env, args) -> int:
    return env.lock(constraint=args.constraint)


def cmd_install(env: Env, args) -> int:
    return env.install()


def cmd_run(env: Env, args) -> int:
    return env.run(args.exe, *args.args)


def cmd_version(env: Env, args) -> int:
    from . import __version__
    print(__version__, file=env.stream)
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
    parser.add_argument('--venvs', default='.venvs')
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
    env = Env(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
        stream=stream,
    )
    return args.func(env=env, args=args)


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stream=sys.stdout))
