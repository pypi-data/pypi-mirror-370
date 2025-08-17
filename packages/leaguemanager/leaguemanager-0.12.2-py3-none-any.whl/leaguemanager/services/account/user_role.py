from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService


class UserRoleSyncService(SQLAlchemySyncRepositoryService):
    """Handles database operations in the user/role association."""

    class Repo(SQLAlchemySyncRepository[m.UserRole]):
        """User repository."""

        model_type = m.UserRole

    repository_type = Repo


class UserRoleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations in the user/role association."""

    class Repo(SQLAlchemyAsyncRepository[m.UserRole]):
        """User repository."""

        model_type = m.UserRole

    repository_type = Repo
