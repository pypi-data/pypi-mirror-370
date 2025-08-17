from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import AthleteStats
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["AthleteStatsService", "AthleteStatsAsyncService"]


class AthleteStatsService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    class Repo(SQLAlchemySyncRepository[AthleteStats]):
        """AthleteStats repository."""

        model_type = AthleteStats

    repository_type = Repo


class AthleteStatsAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    class Repo(SQLAlchemyAsyncRepository[AthleteStats]):
        """AthleteStats repository."""

        model_type = AthleteStats

    repository_type = Repo
