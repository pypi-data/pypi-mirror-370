from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import ManagerMembership
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["ManagerMembershipService", "ManagerMembershipAsyncService"]


class ManagerMembershipService(SQLAlchemySyncRepositoryService):
    """Handles database operations for manager membership data."""

    class Repo(SQLAlchemySyncRepository[ManagerMembership]):
        """ManagerMembership repository."""

        model_type = ManagerMembership

    repository_type = Repo


class ManagerMembershipAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for manager membership data."""

    class Repo(SQLAlchemyAsyncRepository[ManagerMembership]):
        """ManagerMembership repository."""

        model_type = ManagerMembership

    repository_type = Repo
