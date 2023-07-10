from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import Any

import toml

from ._constants import MAIN_ENV


CWD = Path()


def get_envs(root: Path = CWD) -> list[str]:
    """Get names of all environments available in pyproject.toml.
    """
    deps = get_deps(root=root)
    if not deps:
        return [MAIN_ENV]
    return sorted(deps)


def get_deps(root: Path = CWD) -> dict[str, list[str]] | None:
    """Get list of dependencies listed in pyproject.toml for each environment.
    """
    path = root / 'pyproject.toml'
    if not path.exists():
        return None
    with path.open('r', encoding='utf-8') as stream:
        pyproject = toml.load(stream)
    deps = _get_old_flit_deps(pyproject)
    if deps is not None:
        return deps
    return _get_new_deps(pyproject)


def _get_old_flit_deps(pyproject: dict[str, Any]) -> dict[str, list[str]] | None:
    result = {}
    try:
        meta = pyproject['tool']['flit']['metadata']
    except KeyError:
        return None
    with suppress(KeyError):
        result[MAIN_ENV] = meta['requires']
    with suppress(KeyError):
        result.update(meta['requires-extra'])
    return result or None


def _get_new_deps(pyproject: dict[str, Any]) -> dict[str, list[str]] | None:
    result = {}
    try:
        meta = pyproject['project']
    except KeyError:
        return None
    with suppress(KeyError):
        result[MAIN_ENV] = meta['dependencies']
    with suppress(KeyError):
        result.update(meta['optional-dependencies'])
    return result or None
