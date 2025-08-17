from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import TeamMembership
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["TeamMembershipService", "TeamMembershipAsyncService"]


class TeamMembershipService(SQLAlchemySyncRepositoryService):
    """Handles database operations for team membership data."""

    class Repo(SQLAlchemySyncRepository[TeamMembership]):
        """TeamMembership repository."""

        model_type = TeamMembership

    repository_type = Repo


class TeamMembershipAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for team membership data."""

    class Repo(SQLAlchemyAsyncRepository[TeamMembership]):
        """TeamMembership repository."""

        model_type = TeamMembership

    repository_type = Repo
