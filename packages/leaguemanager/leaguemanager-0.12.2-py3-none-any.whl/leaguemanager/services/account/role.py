from __future__ import annotations

from typing import Any

import attrs
from advanced_alchemy import service
from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
    SQLAlchemySyncSlugRepository,
)
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
)

__all__ = ["RoleSyncService", "RoleAsyncService"]


class RoleSyncService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[m.Role]):
        """Role repository."""

        model_type = m.Role

    repository_type = SlugRepo


class RoleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[m.Role]):
        """Role repository."""

        model_type = m.Role

    repository_type = SlugRepo
    match_fields = ["name"]

    async def to_model_on_create(self, data: service.ModelDictT[m.Role]) -> service.ModelDictT[m.Role]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data: service.ModelDictT[m.Role]) -> service.ModelDictT[m.Role]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug") and service.is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_upsert(self, data: service.ModelDictT[m.Role]) -> service.ModelDictT[m.Role]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug") and (role_name := data.get("name")) is not None:
            data["slug"] = await self.repository.get_available_slug(role_name)
        return data
