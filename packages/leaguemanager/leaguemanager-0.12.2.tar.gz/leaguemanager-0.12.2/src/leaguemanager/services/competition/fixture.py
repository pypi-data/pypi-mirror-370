from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Fixture
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["FixtureService", "FixtureAsyncService"]


class FixtureService(SQLAlchemySyncRepositoryService):
    """Handles database operations for fixture data."""

    class Repo(SQLAlchemySyncRepository[Fixture]):
        """Fixture repository."""

        model_type = Fixture

    repository_type = Repo


class FixtureAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for fixture data."""

    class Repo(SQLAlchemyAsyncRepository[Fixture]):
        """Fixture repository."""

        model_type = Fixture

    repository_type = Repo
