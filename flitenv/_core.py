import subprocess
import sys
import typing
from pathlib import Path

import flit
from dephell_venvs import VEnv


MAIN_ENV = 'main'


class Env(typing.NamedTuple):
    root: Path
    name: str
    venvs: str = '.venvs'
    stream: typing.TextIO = sys.stdout

    @property
    def path(self) -> Path:
        path = Path(self.venvs)
        if path.is_absolute():
            return path / self.name
        return self.root / self.venvs / self.name

    def _pip_install(self, *args):
        venv = VEnv(path=self.path)
        cmd = [str(venv.python_path), '-m', 'pip', 'install']
        cmd.extend(args)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
        result.check_returncode()

    @property
    def constraint(self) -> Path:
        name = 'requirements.txt'
        if self.name != MAIN_ENV:
            name = f'requirements-{self.name}.txt'
        return self.root / name

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
        constr = self.constraint
        if constr.exists():
            print('installing requirements.txt...', file=self.stream)
            self._pip_install('-r', str(constr))

        try:
            cmd = [
                'install',
                '--python', str(venv.python_path),
                '--deps', 'production',
                '--symlink',
            ]
            if self.name != MAIN_ENV:
                cmd.extend(['--extras', self.name])
            print('installing project deps...', file=self.stream)
            flit.main(cmd)
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

    def lock(self, constraint: str) -> int:
        tmp = Path('_tmp_requirements.in')
        if constraint:
            tmp.write_text(f'-c {constraint}')
        cmd = [
            sys.executable, '-m', 'piptools', 'compile',
            '--annotate',
            '--generate-hashes',
            '--no-header',
            '--no-emit-index-url',
            '--output-file', str(self.constraint),
            'pyproject.toml',
        ]
        if self.name != MAIN_ENV:
            cmd.extend(['--extra', self.name])
        if constraint:
            cmd.append(str(tmp))

        result = subprocess.run(cmd)
        if constraint:
            tmp.unlink()
        return result.returncode
