from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import IndividualMembership
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["IndividualMembershipService", "IndividualMembershipAsyncService"]


class IndividualMembershipService(SQLAlchemySyncRepositoryService):
    """Handles database operations for individual membership data."""

    class Repo(SQLAlchemySyncRepository[IndividualMembership]):
        """Individual membership repository."""

        model_type = IndividualMembership

    repository_type = Repo


class IndividualMembershipAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for individual membership data."""

    class Repo(SQLAlchemyAsyncRepository[IndividualMembership]):
        """Individual membership repository."""

        model_type = IndividualMembership

    repository_type = Repo
