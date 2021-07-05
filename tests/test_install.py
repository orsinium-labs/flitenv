import subprocess
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
    assert project.joinpath('.venvs', 'test', 'bin', 'pytest').exists()


def test_install_test_with_lockfile(project: Path) -> None:
    (project / 'requirements.txt').write_text('pytest==6.2.1')
    cmd = ['--root', str(project), 'test', 'install']
    main(argv=cmd, stream=sys.stdout)
    pytest_path = project.joinpath('.venvs', 'test', 'bin', 'pytest')
    assert pytest_path.exists()
    result = subprocess.run([str(pytest_path), '--version'], capture_output=True)
    assert result.returncode == 0
    assert result.stderr.decode() == 'pytest 6.2.1\n'
