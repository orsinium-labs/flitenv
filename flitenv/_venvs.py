from __future__ import annotations

from pathlib import Path
from typing import Any

import toml

from ._constants import MAIN_ENV


def get_envs() -> list[str] | None:
    path = Path('pyproject.toml')
    if not path.exists():
        return None
    with path.open('r', encoding='utf-8') as stream:
        pyproject = toml.load(stream)
    envs = _get_old_flit_extras(pyproject)
    if envs is None:
        envs = _get_new_extras(pyproject)
    if envs is None:
        return [MAIN_ENV]
    return [MAIN_ENV, *sorted(envs)]


def _get_old_flit_extras(pyproject: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return pyproject['tool']['flit']['metadata']['requires-extra']
    except KeyError:
        return None


def _get_new_extras(pyproject: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return pyproject['project']['optional-dependencies']
    except KeyError:
        return None
