from __future__ import annotations

from advanced_alchemy import service
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository

from leaguemanager import models as m


class TagService(service.SQLAlchemySyncRepositoryService[m.Tag]):
    """Handles basic lookup operations for an Tag."""

    class Repo(SQLAlchemySyncSlugRepository[m.Tag]):
        """Tag Repository."""

        model_type = m.Tag

    repository_type = Repo


class TagAsyncService(service.SQLAlchemyAsyncRepositoryService[m.Tag]):
    """Handles basic lookup operations for an Tag."""

    class Repo(SQLAlchemyAsyncSlugRepository[m.Tag]):
        """Tag Repository."""

        model_type = m.Tag

    repository_type = Repo
    match_fields = ["name"]

    async def to_model_on_create(self, data: service.ModelDictT[m.Tag]) -> service.ModelDictT[m.Tag]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data: service.ModelDictT[m.Tag]) -> service.ModelDictT[m.Tag]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug") and service.is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_upsert(self, data: service.ModelDictT[m.Tag]) -> service.ModelDictT[m.Tag]:
        data = service.schema_dump(data)
        if service.is_dict_without_field(data, "slug") and (tag_name := data.get("name")) is not None:
            data["slug"] = await self.repository.get_available_slug(tag_name)
        return data
