from __future__ import annotations

import json
from argparse import ArgumentParser

from .._meta import get_deps, get_envs
from ._base import Command


class Deps(Command):
    """List direct dependencies for the given environment (or all environments).
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            'env', choices=get_envs(), nargs='?',
            help='The environment for which to list deps.',
        )

    def run(self) -> int:
        deps = get_deps(root=self.args.root)
        if not deps:
            return 1
        if self.args.env:
            self.print(*deps[self.args.env], sep='\n')
        else:
            self.print(json.dumps(deps, indent=2))
        return 0
