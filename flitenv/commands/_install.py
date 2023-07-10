from __future__ import annotations

from ._base import Command


class Install(Command):
    """Install dependencies in the given environment.
    """

    def run(self) -> int:
        return self.deps.install()
