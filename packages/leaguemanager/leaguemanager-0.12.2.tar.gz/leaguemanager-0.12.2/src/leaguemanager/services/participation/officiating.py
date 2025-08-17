from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Officiating
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["OfficiatingService", "OfficiatingAsyncService"]


class OfficiatingService(SQLAlchemySyncRepositoryService):
    """Handles database operations for officiating data."""

    class Repo(SQLAlchemySyncRepository[Officiating]):
        """Officiating repository."""

        model_type = Officiating

    repository_type = Repo


class OfficiatingAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for officiating data."""

    class Repo(SQLAlchemyAsyncRepository[Officiating]):
        """Officiating repository."""

        model_type = Officiating

    repository_type = Repo
