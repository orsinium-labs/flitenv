from __future__ import annotations

import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

from .commands import Command, commands


def main(argv: list[str], stdout: typing.TextIO) -> int:
    parser = ArgumentParser('mypy-baseline')
    parser.add_argument(
        '--root', type=Path, default=Path(),
        help='Path to the project root.',
    )
    parser.add_argument(
        '--venvs', type=Path,
        help='Path to venvs directory. Defaults to .venvs in the project root.',
    )
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)

    cmd_class: type[Command]
    for name, cmd_class in sorted(commands.items()):
        subparser = subparsers.add_parser(name=name, help=cmd_class.__doc__)
        subparser.set_defaults(cmd=cmd_class)
        cmd_class.init_parser(subparser)
    args = parser.parse_args(argv)

    cmd_class = args.cmd
    if cmd_class is None:
        parser.print_help()
        return 1
    cmd = cmd_class(args=args, stdout=stdout)
    return cmd.run()


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stdout=sys.stdout))
