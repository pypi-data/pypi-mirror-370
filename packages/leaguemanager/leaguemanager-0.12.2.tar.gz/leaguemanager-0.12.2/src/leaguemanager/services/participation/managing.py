from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Managing
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["ManagingService", "ManagingAsyncService"]


class ManagingService(SQLAlchemySyncRepositoryService):
    """Handles database operations for "managing" data."""

    class Repo(SQLAlchemySyncRepository[Managing]):
        """Managing repository."""

        model_type = Managing

    repository_type = Repo


class ManagingAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for "managing" data."""

    class Repo(SQLAlchemyAsyncRepository[Managing]):
        """Managing repository."""

        model_type = Managing

    repository_type = Repo
