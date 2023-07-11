from __future__ import annotations

from argparse import ArgumentParser

from .._constants import MAIN_ENV
from .._deps_manager import DepsManager
from .._meta import get_deps
from .._venv import VEnv
from ._base import Command


class Run(Command):
    """Run a command in the given environment.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            'env_or_exe',
            help='environment name and executable (or only executable) to run',
        )
        parser.add_argument('args', nargs='...')

    def run(self) -> int:
        # detect environment, executable, and executable args
        env: str = self.args.env_or_exe
        exe_args: list[str] = self.args.args
        deps = get_deps()
        if deps and env in deps:
            if not exe_args:
                self.print('Error: executable name is required')
                return 1
            exe = exe_args[0]
            exe_args = exe_args[1:]
        else:
            exe = env
            env = self._detect_env(deps, exe)

        venv = VEnv(
            name=env,
            root=self.args.root,
            venvs=self.args.venvs,
        )
        deps_manager = DepsManager(
            root=self.args.root,
            venv=venv,
            stream=self.stdout,
        )
        return deps_manager.run(exe, *exe_args)

    def _detect_env(
        self,
        deps: dict[str, list[str]] | None,
        exe: str,
    ) -> str:
        if deps is None:
            return MAIN_ENV
        for env, env_deps in deps.items():
            if exe in env_deps:
                return env
        return MAIN_ENV
