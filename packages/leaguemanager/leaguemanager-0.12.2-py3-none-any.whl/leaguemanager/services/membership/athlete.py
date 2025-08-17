from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Athlete
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["AthleteService", "AthleteAsyncService"]


class AthleteService(SQLAlchemySyncRepositoryService):
    """Handles database operations for athlete data."""

    class Repo(SQLAlchemySyncRepository[Athlete]):
        """Athlete repository."""

        model_type = Athlete

    repository_type = Repo


class AthleteAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for athlete data."""

    class Repo(SQLAlchemyAsyncRepository[Athlete]):
        """Athlete repository."""

        model_type = Athlete

    repository_type = Repo
