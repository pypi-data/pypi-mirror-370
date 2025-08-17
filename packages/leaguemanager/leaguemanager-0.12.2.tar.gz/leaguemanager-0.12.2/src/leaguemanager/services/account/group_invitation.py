from __future__ import annotations

from advanced_alchemy import service
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository

from leaguemanager import models as m


class GroupInvitationService(service.SQLAlchemySyncRepositoryService[m.GroupInvitation]):
    """Handles basic lookup operations for an GroupInvitation."""

    class Repo(SQLAlchemySyncSlugRepository[m.GroupInvitation]):
        """GroupInvitation Repository."""

        model_type = m.GroupInvitation

    repository_type = Repo


class GroupInvitationAsyncService(service.SQLAlchemyAsyncRepositoryService[m.GroupInvitation]):
    """Handles basic lookup operations for an GroupInvitation."""

    class Repo(SQLAlchemyAsyncSlugRepository[m.GroupInvitation]):
        """GroupInvitation Repository."""

        model_type = m.GroupInvitation

    repository_type = Repo
