import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent


@pytest.fixture
def project(tmp_path: Path) -> Path:
    src = ROOT / 'pyproject.toml'
    dst = tmp_path / 'pyproject.toml'
    dst.write_text(src.read_text())
    return tmp_path
