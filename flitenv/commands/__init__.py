from __future__ import annotations

from types import MappingProxyType

from ._base import Command
from ._deps import Deps
from ._install import Install
from ._lock import Lock
from ._run import Run
from ._version import Version


commands: MappingProxyType[str, type[Command]]
commands = MappingProxyType({
    'deps': Deps,
    'install': Install,
    'lock': Lock,
    'run': Run,
    'version': Version,
})

__all__ = [
    'commands',
    'Command',
]
