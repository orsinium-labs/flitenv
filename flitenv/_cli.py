import subprocess
import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

from ._core import Env


def cmd_lock(args, stream: typing.TextIO) -> int:
    tmp = Path('_tmp_requirements.in')
    if args.constraint:
        tmp.write_text(f'-c {args.constraint}')
    cmd = [
        sys.executable, '-m', 'piptools', 'compile',
        '--annotate',
        '--generate-hashes',
        '--no-header',
        '--no-emit-index-url',
        '--output-file', 'requirements.txt',
        'pyproject.toml',
    ]
    if args.constraint:
        cmd.append(str(tmp))

    result = subprocess.run(cmd)
    if args.constraint:
        tmp.unlink()
    return result.returncode


def cmd_install(args, stream: typing.TextIO) -> int:
    env = Env(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
        stream=stream,
    )
    return env.install()


def cmd_run(args, stream: typing.TextIO) -> int:
    env = Env(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
        stream=stream,
    )
    return env.run(args.exe, *args.args)


def main(argv: typing.List[str], stream: typing.TextIO) -> int:

    parser = ArgumentParser()
    parser.format_help
    parser.add_argument('env')
    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser(
        name='install',
        help='install env dependencies',
    )
    install_parser.add_argument('--root', type=Path, default=Path())
    install_parser.add_argument('--venvs', default='.venvs')
    install_parser.set_defaults(func=cmd_install)

    run_parser = subparsers.add_parser(
        name='run',
        help='run a command inside the env',
    )
    run_parser.add_argument('--root', type=Path, default=Path())
    run_parser.add_argument('--venvs', default='.venvs')
    run_parser.add_argument('exe')
    run_parser.add_argument('args', nargs='...')
    run_parser.set_defaults(func=cmd_run)

    lock_parser = subparsers.add_parser(
        name='lock',
        help='generate lock file',
    )
    lock_parser.add_argument('-c', '--constraint')
    lock_parser.set_defaults(func=cmd_lock)

    args = parser.parse_args(argv)
    return args.func(args=args, stream=stream)


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stream=sys.stdout))
