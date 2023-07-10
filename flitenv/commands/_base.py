from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import ClassVar, TextIO


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
