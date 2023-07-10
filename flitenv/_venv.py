from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from functools import cached_property
from pathlib import Path

from ._constants import IS_WINDOWS, VENVS


@dataclasses.dataclass(frozen=True)
class VEnvState:
    deps: list[str]
    lock_hash: str | None = None

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class VEnv:
    root: Path
    name: str
    venvs: Path | None = None
    system_python: Path = Path(sys.executable)

    @cached_property
    def path(self) -> Path:
        if self.venvs is None:
            return self.root / VENVS / self.name
        return self.venvs.absolute() / self.name

    @cached_property
    def bin_path(self) -> Path:
        if IS_WINDOWS:
            return self.path / 'Scripts'
        return self.path / 'bin'

    @cached_property
    def python_path(self) -> Path | None:
        if self.bin_path is None:
            return None
        executables = {path.name for path in self.bin_path.iterdir()}
        for implementation in ('pypy', 'python', 'pypy3', 'python3'):
            for ext in ('', '.exe'):
                path = self.bin_path / f'{implementation}{ext}'
                if path.name in executables:
                    return path
        return None

    @property
    def exists(self) -> bool:
        return self.bin_path.exists()

    def read_state(self) -> VEnvState | None:
        path = self.path / 'flitenv.json'
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding='utf8'))
        return VEnvState(**data)

    def write_state(self, state: VEnvState) -> None:
        path = self.path / 'flitenv.json'
        data = json.dumps(state.as_dict())
        path.write_text(data, encoding='utf8')

    def create(self) -> None:
        cmd = [str(self.system_python), '-m', 'venv', str(self.path)]
        subprocess.run(cmd)

    def _reset_cache(self) -> None:
        v = vars(self)
        v.pop('path', '')
        v.pop('bin_path', '')
        v.pop('python_path', '')
