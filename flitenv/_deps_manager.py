from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import flit

from ._constants import MAIN_ENV
from ._meta import get_deps
from ._venv import VEnv, VEnvState


@contextmanager
def update_env(**kwargs: str):
    old_env = dict(os.environ)
    os.environ.update(kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)


@dataclass(frozen=True)
class DepsManager:
    root: Path
    venv: VEnv
    stream: TextIO = sys.stdout

    def _pip_install(self, *args: str) -> None:
        """Execute `pip install` in the environment.
        """
        cmd = [str(self.venv.python_path), '-m', 'pip', 'install']
        cmd.extend(args)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
        result.check_returncode()

    def _get_constraint(self, env_name: str | None = None) -> Path:
        """Get path to the lock file (constraints).

        Tries to use environment-specific lock, if available.
        Otherwise, defaults to the main env lock file.
        """
        if not env_name:
            env_name = self.venv.name
        name = 'requirements.txt'
        if env_name != MAIN_ENV:
            name = f'requirements-{env_name}.txt'
        return self.root / name

    @property
    def deps(self) -> list[str]:
        """Get from metadata list of dependencies that needs to be in this env.
        """
        deps = get_deps(root=self.root)
        if not deps:
            return []
        main_deps = deps.get(MAIN_ENV, [])
        env_deps = deps.get(self.venv.name, [])
        return sorted(main_deps + env_deps)

    @property
    def synced(self) -> bool:
        """Check if all dependencies in the venv are up to date with metadata.
        """
        # if the state dump file isn't here, we never synced
        state = self.venv.read_state()
        if state is None:
            return False
        # check if dependencies has changed
        if state.deps != self.deps:
            return False
        return state.lock_hash == self.lock_hash

    @property
    def lock_hash(self) -> str | None:
        """MD5 hash of the lock file (constraints).
        """
        constr = self._get_constraint()
        if not constr.exists():
            constr = self._get_constraint(MAIN_ENV)
        if not constr.exists():
            return None
        content = constr.read_bytes()
        return hashlib.md5(content).hexdigest()

    def install(self) -> int:
        # create venv if does not exist
        if not self.venv.exists:
            print('creating venv...', file=self.stream)
            self.venv.create()

        # install wheel if not installed
        if not (self.venv.bin_path / 'wheel').exists():
            print('installing wheel...', file=self.stream)
            self._pip_install('-U', 'pip', 'wheel', 'setuptools')

        # use lock file (constraints) if available
        env = {}
        constr = self._get_constraint()
        if not constr.exists():
            constr = self._get_constraint(MAIN_ENV)
        if constr.exists():
            env['PIP_CONSTRAINT'] = str(constr)

        # install dependencies with flit
        try:
            cmd = [
                'install',
                '--python', str(self.venv.python_path),
                '--deps', 'production',
                '--symlink',
            ]
            if self.venv.name != MAIN_ENV:
                cmd.extend(['--extras', self.venv.name])
            print('installing project deps...', file=self.stream)
            with update_env(**env):
                flit.main(cmd)
        except SystemExit as exc:
            return int(exc.code or 1)

        # update the state dump
        self.venv.write_state(VEnvState(
            deps=self.deps,
            lock_hash=self.lock_hash,
        ))
        return 0

    def run(self, exe: str, *cmd: str) -> int:
        if not self.synced:
            code = self.install()
            if code != 0:
                return code

        exe_path = self.venv.bin_path / exe
        if exe_path.exists():
            full_cmd = [str(exe_path)]
        else:
            full_cmd = [str(self.venv.python_path), '-m', exe]
        full_cmd.extend(cmd)
        try:
            result = subprocess.run(full_cmd)
        except KeyboardInterrupt:
            print('KeyboardInterrupt', file=self.stream)
            return 1
        return result.returncode

    def lock(self, constraint: str) -> int:
        tmp = Path('_tmp_requirements.in')
        if constraint:
            tmp.write_text(f'-c {constraint}')
        cmd = [
            sys.executable, '-m', 'piptools', 'compile',
            '--annotate',
            '--no-header',
            '--no-emit-index-url',
            '--strip-extras',
            '--output-file', str(self._get_constraint()),
            'pyproject.toml',
        ]
        if self.venv.name != MAIN_ENV:
            cmd.extend(['--extra', self.venv.name])
        if constraint:
            cmd.append(str(tmp))

        result = subprocess.run(cmd)
        if constraint:
            tmp.unlink()
        return result.returncode
