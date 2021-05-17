import subprocess
import sys
import typing
from argparse import ArgumentParser
from pathlib import Path

from ._core import Env


def lock(constr: Path) -> int:
    tmp = Path('_tmp_requirements.in')
    tmp.write_text(f'-c {constr}')
    cmd = [
        sys.executable, '-m', 'piptools', 'compile',
        '--annotate',
        '--generate-hashes',
        '--no-header',
        '--no-emit-index-url',
        '--output-file', 'requirements.txt',
        str(tmp),
        'pyproject.toml',
    ]
    result = subprocess.run(cmd)
    tmp.unlink()
    return result.returncode


def main(argv: typing.List[str], stream: typing.TextIO) -> int:
    if argv and argv[0] == 'lock':
        parser = ArgumentParser()
        parser.add_argument('constr')
        args = parser.parse_args(argv[1:])
        return lock(args.constr)

    parser = ArgumentParser()
    parser.add_argument('env')
    parser.add_argument('cmd', choices=['install', 'run'])
    parser.add_argument('--root', type=Path, default=Path())
    parser.add_argument('--venvs', default='.venvs')
    args, _ = parser.parse_known_args(argv)
    env = Env(
        name=args.env,
        root=args.root,
        venvs=args.venvs,
        stream=stream,
    )

    if args.cmd == 'install':
        args = parser.parse_args(argv)
        return env.install()
    if args.cmd == 'run':
        parser.add_argument('exe')
        parser.add_argument('args', nargs='...')
        args = parser.parse_args(argv)
        return env.run(args.exe, *args.args)
    raise RuntimeError('unreachable')


def entrypoint() -> typing.NoReturn:
    sys.exit(main(sys.argv[1:], stream=sys.stdout))
