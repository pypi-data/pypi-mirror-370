from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Official
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["OfficialService", "OfficialAsyncService"]


class OfficialService(SQLAlchemySyncRepositoryService):
    """Handles database operations for official data."""

    class Repo(SQLAlchemySyncRepository[Official]):
        """Official repository."""

        model_type = Official

    repository_type = Repo


class OfficialAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for official data."""

    class Repo(SQLAlchemyAsyncRepository[Official]):
        """Official repository."""

        model_type = Official

    repository_type = Repo
