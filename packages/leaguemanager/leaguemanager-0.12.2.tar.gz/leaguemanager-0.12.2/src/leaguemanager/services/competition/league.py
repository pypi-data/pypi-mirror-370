from __future__ import annotations

from typing import Any

import attrs
from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository
from sqlalchemy import select

from leaguemanager.models import League
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
)

__all__ = ["LeagueService", "LeagueAsyncService"]


class LeagueService(SQLAlchemySyncRepositoryService):
    """Handles database operations for league data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[League]):
        """League repository."""

        model_type = League

    repository_type = SlugRepo

    def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data

    def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data


class LeagueAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for league data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[League]):
        """League repository."""

        model_type = League

    repository_type = SlugRepo

    async def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data
