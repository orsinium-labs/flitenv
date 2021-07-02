import sys
from pathlib import Path
from flitenv._cli import main


def test_lock_main(project: Path) -> None:
    cmd = ['--root', str(project), 'main', 'lock']
    main(argv=cmd, stream=sys.stdout)
    print(list(project.iterdir()))
    path = project / 'requirements.txt'
    assert path.is_file()
    content = path.read_text()
    assert 'pip-tools' in content
    assert 'pytest' not in content


def test_lock_test(project: Path) -> None:
    cmd = ['--root', str(project), 'test', 'lock']
    main(argv=cmd, stream=sys.stdout)
    print(list(project.iterdir()))
    path = project / 'requirements-test.txt'
    assert path.is_file()
    content = path.read_text()
    assert 'pip-tools' in content
    assert 'pytest' in content
