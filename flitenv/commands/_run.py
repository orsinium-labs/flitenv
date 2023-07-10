from __future__ import annotations

from argparse import ArgumentParser

from ._base import Command


class Run(Command):
    """Run a command in the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        Command.init_parser(parser)
        parser.add_argument('exe')
        parser.add_argument('args', nargs='...')

    def run(self) -> int:
        return self.deps.run(self.args.exe, *self.args.args)
