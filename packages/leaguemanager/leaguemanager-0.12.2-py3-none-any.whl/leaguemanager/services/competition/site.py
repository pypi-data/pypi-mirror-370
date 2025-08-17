from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository
from sqlalchemy import select

from leaguemanager.models import Site
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["SiteService", "SiteAsyncService"]


class SiteService(SQLAlchemySyncRepositoryService):
    """Handles database operations for site data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[Site]):
        """Site repository."""

        model_type = Site

    repository_type = SlugRepo


class SiteAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for site data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[Site]):
        """Site repository."""

        model_type = Site

    repository_type = SlugRepo
