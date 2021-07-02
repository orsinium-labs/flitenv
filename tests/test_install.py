import sys
from pathlib import Path
from flitenv._cli import main


def test_install_main(project: Path) -> None:
    cmd = ['--root', str(project), 'main', 'install']
    main(argv=cmd, stream=sys.stdout)
    print(list(project.iterdir()))
    assert (project / '.venvs' / 'main' / 'bin').is_dir()


def test_install_test(project: Path) -> None:
    cmd = ['--root', str(project), 'test', 'install']
    main(argv=cmd, stream=sys.stdout)
    print(list(project.iterdir()))
    assert (project / '.venvs' / 'test' / 'bin').is_dir()
