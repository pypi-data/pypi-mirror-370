from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import Ruleset
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["RulesetService", "RulesetAsyncService"]


class RulesetService(SQLAlchemySyncRepositoryService):
    """Handles database operations for ruleset data."""

    class Repo(SQLAlchemySyncRepository[Ruleset]):
        """Ruleset repository."""

        model_type = Ruleset

    repository_type = Repo


class RulesetAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for ruleset data."""

    class Repo(SQLAlchemyAsyncRepository[Ruleset]):
        """Ruleset repository."""

        model_type = Ruleset

    repository_type = Repo
