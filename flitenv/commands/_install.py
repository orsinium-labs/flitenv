from __future__ import annotations

from argparse import ArgumentParser

from .._constants import MAIN_ENV
from .._deps_manager import DepsManager
from .._meta import get_envs
from .._venv import VEnv
from ._base import Command


class Install(Command):
    """Install dependencies in the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            'env', choices=get_envs(), nargs='?',
            help='The environment in which to install deps.',
        )
        parser.add_argument(
            '-f', '--force', action='store_true',
            help='try to install dependencies even if up to date',
        )

    def run(self) -> int:
        venv = VEnv(
            name=self.args.env or MAIN_ENV,
            root=self.args.root,
            venvs=self.args.venvs,
        )
        deps = DepsManager(
            root=self.args.root,
            venv=venv,
            stream=self.stdout,
        )
        if not self.args.force and deps.synced:
            self.print('Already in sync')
            return 0
        return deps.install()
