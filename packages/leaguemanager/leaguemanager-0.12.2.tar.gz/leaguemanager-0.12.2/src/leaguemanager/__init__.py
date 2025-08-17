"""Metadata for CLI tool."""

__app_name__ = "mgr"


from leaguemanager.__metadata__ import __version__
from leaguemanager.dependency import LeagueManager

__all__ = ["__app_name__", "__version__", "LeagueManager"]
