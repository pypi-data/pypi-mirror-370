from __future__ import annotations

from advanced_alchemy import service
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository

from leaguemanager import models as m


class GroupMemberervice(service.SQLAlchemySyncRepositoryService[m.GroupMember]):
    """Handles basic lookup operations for an GroupMember."""

    class Repo(SQLAlchemySyncSlugRepository[m.GroupMember]):
        """GroupMember Repository."""

        model_type = m.GroupMember

    repository_type = Repo


class GroupMemberAsyncService(service.SQLAlchemyAsyncRepositoryService[m.GroupMember]):
    """Handles basic lookup operations for an GroupMember."""

    class Repo(SQLAlchemyAsyncSlugRepository[m.GroupMember]):
        """GroupMember Repository."""

        model_type = m.GroupMember

    repository_type = Repo
