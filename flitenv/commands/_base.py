from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, TextIO

from .._deps_manager import DepsManager
from .._venv import VEnv


@dataclass
class Command:
    name: ClassVar[str]
    args: Namespace
    stdout: TextIO

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        pass

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
