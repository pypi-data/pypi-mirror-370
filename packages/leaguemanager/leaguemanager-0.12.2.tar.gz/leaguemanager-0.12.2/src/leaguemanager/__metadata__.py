"""Metadata for the Project."""

from __future__ import annotations

import importlib.metadata

__all__ = ("__project__", "__version__")

__version__ = importlib.metadata.version("leaguemanager")
"""Version of the project."""
__project__ = importlib.metadata.metadata("leaguemanager")["Name"]
"""Name of the project."""
