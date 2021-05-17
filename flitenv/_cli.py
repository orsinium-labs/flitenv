import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

from ._core import Env


def main(argv: typing.List[str], stream: typing.TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('env')
    parser.add_argument('cmd', choices=['install', 'run'])
    parser.add_argument('--root', type=Path, default=Path())
    parser.add_argument('--venvs', default='.venvs')
    args, _ = parser.parse_known_args(argv)
    env = Env(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
        stream=stream,
    )

    if args.cmd == 'install':
        args = parser.parse_args(argv)
        return env.install()
    if args.cmd == 'run':
        parser.add_argument('args', nargs='+')
        args = parser.parse_args(argv)
        return env.run(*args.args)
    raise RuntimeError('unreachable')


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stream=sys.stdout))
