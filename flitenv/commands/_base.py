from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import ClassVar, TextIO

from .._deps_manager import DepsManager
from .._venv import VEnv
from .._venvs import get_envs


@dataclass
class Command:
    name: ClassVar[str]
    args: Namespace
    stdout: TextIO

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument('env', choices=get_envs())
        parser.add_argument('--venvs', type=Path)

    def run(self) -> int:
        raise NotImplementedError

    def print(self, *args: str, end: str = '\n', sep: str = ' ') -> None:
        print(*args, file=self.stdout, end=end, sep=sep)

    @cached_property
    def venv(self) -> VEnv:
        return VEnv(
            name=self.args.env,
            root=self.args.root,
            venvs=self.args.venvs,
        )

    @cached_property
    def deps(self) -> DepsManager:
        return DepsManager(
            root=self.args.root,
            venv=self.venv,
            stream=self.stdout,
        )
