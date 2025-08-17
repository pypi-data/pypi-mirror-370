from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import TeamStats
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["TeamStatsService", "TeamStatsAsyncService"]


class TeamStatsService(SQLAlchemySyncRepositoryService):
    """Handles database operations for team stats data."""

    class Repo(SQLAlchemySyncRepository[TeamStats]):
        """TeamStats repository."""

        model_type = TeamStats

    repository_type = Repo


class TeamStatsAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for team stats data."""

    class Repo(SQLAlchemySyncRepository[TeamStats]):
        """TeamStats repository."""

        model_type = TeamStats

    repository_type = Repo
