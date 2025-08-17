from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository
from sqlalchemy import select

from leaguemanager.models import Team
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["TeamService", "TeamAsyncService"]


class TeamService(SQLAlchemySyncRepositoryService):
    """Handles database operations for team data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[Team]):
        """Team repository."""

        model_type = Team

    repository_type = SlugRepo


class TeamAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for team data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[Team]):
        """Team repository."""

        model_type = Team

    repository_type = SlugRepo
