from datetime import datetime
from importlib.util import find_spec
from pathlib import Path

from advanced_alchemy.utils.text import slugify
from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager.models.base import UUIDBase

__all__ = ["slugify", "clear_table", "str_to_iso", "module_to_os_path"]


def clear_table(session: Session, model: UUIDBase) -> None:
    """Clears table of given model."""
    session.execute(delete(model))


def str_to_iso(date_string: str, format: str):
    """Converts string to datetime object."""
    return datetime.strptime(date_string, format)


def module_to_os_path(module_name: str) -> Path:
    """Get the string path of the module."""
    spec = find_spec(module_name)
    if not spec:
        raise ValueError(f"Couldn't find path for {module_name}")
    return Path(spec.origin).parent.resolve()
