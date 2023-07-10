from __future__ import annotations

from argparse import ArgumentParser

from .._constants import MAIN_ENV
from .._deps_manager import DepsManager
from .._meta import get_envs
from .._venv import VEnv
from ._base import Command


class Lock(Command):
    """Generate lock file for the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            'env', choices=get_envs(), nargs='?',
            help='The environment in which to lock deps.',
        )
        parser.add_argument(
            '-c', '--constraint',
            help='Optional path to a constraint file.',
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
        return deps.lock(constraint=self.args.constraint)
