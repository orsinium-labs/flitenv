from __future__ import annotations

from argparse import ArgumentParser

from .._venvs import get_envs
from ._base import Command


class Lock(Command):
    """Generate lock file for the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('env', choices=get_envs())
        parser.add_argument('-c', '--constraint')

    def run(self) -> int:
        return self.deps.lock(constraint=self.args.constraint)
