import sys
from pathlib import Path
from flitenv._cli import main


def test_lock(project: Path) -> None:
    cmd = ['--root', str(project), 'main', 'lock']
    main(argv=cmd, stream=sys.stdout)
    print(list(project.iterdir()))
    assert (project / 'requirements.txt').is_file()
