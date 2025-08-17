from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import LeagueProperties
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["LeaguePropertiesService", "LeaguePropertiesAsyncService"]


class LeaguePropertiesService(SQLAlchemySyncRepositoryService):
    """Handles database operations for league properties data."""

    class Repo(SQLAlchemySyncRepository[LeagueProperties]):
        """LeagueProperties repository."""

        model_type = LeagueProperties

    repository_type = Repo


class LeaguePropertiesAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for league properties data."""

    class Repo(SQLAlchemyAsyncRepository[LeagueProperties]):
        """LeagueProperties repository."""

        model_type = LeagueProperties

    repository_type = Repo
