from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Manager
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["ManagerService", "ManagerAsyncService"]


class ManagerService(SQLAlchemySyncRepositoryService):
    """Handles database operations for manager data."""

    class Repo(SQLAlchemySyncRepository[Manager]):
        """Manager repository."""

        model_type = Manager

    repository_type = Repo


class ManagerAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for manager data."""

    class Repo(SQLAlchemyAsyncRepository[Manager]):
        """Manager repository."""

        model_type = Manager

    repository_type = Repo
