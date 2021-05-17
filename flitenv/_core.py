import subprocess
import sys
import typing
from pathlib import Path

import flit
from dephell_venvs import VEnv


class Env(typing.NamedTuple):
    root: Path
    name: str
    venvs: str = '.venvs'
    stream: typing.TextIO = sys.stdout

    @property
    def path(self) -> Path:
        return self.root / self.venvs / self.name

    def _pip_install(self, *args):
        venv = VEnv(path=self.path)
        cmd = [str(venv.python_path), '-m', 'pip', 'install', '-U']
        cmd.extend(args)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
        result.check_returncode()

    def install(self) -> int:
        venv = VEnv(path=self.path)
        if not venv.exists():
            print('creating venv...', file=self.stream)
            venv.create()

        bin_path = venv.bin_path
        assert bin_path
        if not (bin_path / 'wheel').exists():
            print('installing wheel...', file=self.stream)
            self._pip_install('pip', 'wheel', 'setuptools')
        constr = self.root / 'requirements.txt'
        if constr.exists():
            print('installing requirements.txt...', file=self.stream)
            self._pip_install('-r', str(constr))

        try:
            print('installing project deps...', file=self.stream)
            flit.main([
                'install',
                '--python', str(venv.python_path),
                '--deps', 'production',
                '--extras', self.name,
                '--symlink',
            ])
        except SystemExit as exc:
            return exc.code
        return 0

    def run(self, exe, *cmd: str) -> int:
        venv = VEnv(path=self.path)
        bin_path = venv.bin_path
        if not bin_path:
            code = self.install()
            if code != 0:
                return code

        venv = VEnv(path=self.path)
        bin_path = venv.bin_path
        assert bin_path
        full_cmd = [str(bin_path / exe)]
        full_cmd.extend(cmd)
        result = subprocess.run(full_cmd)
        return result.returncode
