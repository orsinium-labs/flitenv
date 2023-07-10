from __future__ import annotations

from argparse import ArgumentParser

from .._constants import MAIN_ENV
from .._deps_manager import DepsManager
from .._venv import VEnv
from .._venvs import get_envs
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
        return deps.install()
