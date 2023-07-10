from __future__ import annotations

from argparse import ArgumentParser

from .._venvs import get_envs
from ._base import Command


class Install(Command):
    """Install dependencies in the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('env', choices=get_envs())

    def run(self) -> int:
        return self.deps.install()
