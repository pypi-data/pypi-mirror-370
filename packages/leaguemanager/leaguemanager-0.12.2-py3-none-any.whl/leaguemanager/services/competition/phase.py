from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Phase
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["PhaseService", "PhaseAsyncService"]


class PhaseService(SQLAlchemySyncRepositoryService):
    """Handles database operations for phase data."""

    class Repo(SQLAlchemySyncRepository[Phase]):
        """Phase repository."""

        model_type = Phase

    repository_type = Repo


class PhaseAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for phase data."""

    class Repo(SQLAlchemyAsyncRepository[Phase]):
        """Phase repository."""

        model_type = Phase

    repository_type = Repo
