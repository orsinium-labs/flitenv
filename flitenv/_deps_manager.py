import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import flit

from ._constants import MAIN_ENV
from ._venv import VEnv


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
        cmd = [str(self.venv.python_path), '-m', 'pip', 'install']
        cmd.extend(args)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
        result.check_returncode()

    def _get_constraint(self, env_name: str = '') -> Path:
        if not env_name:
            env_name = self.venv.name
        name = 'requirements.txt'
        if env_name != MAIN_ENV:
            name = f'requirements-{env_name}.txt'
        return self.root / name

    def install(self) -> int:
        # create venv if does not exist
        if not self.venv.exists:
            print('creating venv...', file=self.stream)
            self.venv.create()

        # install wheel if not installed
        if not (self.venv.bin_path / 'wheel').exists():
            print('installing wheel...', file=self.stream)
            self._pip_install('-U', 'pip', 'wheel', 'setuptools')

        # use constraints file if available
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
            return exc.code
        return 0

    def run(self, exe, *cmd: str) -> int:
        bin_path = self.venv.bin_path
        if not bin_path:
            code = self.install()
            if code != 0:
                return code

        full_cmd = [str(self.venv.bin_path / exe)]
        full_cmd.extend(cmd)
        result = subprocess.run(full_cmd)
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
