from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.lib.toolbox import slugify
from leaguemanager.models.base import UUIDAuditBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from collections.abc import Hashable

    from .role import Role
    from .user import User


@define(slots=False)
class Tag(UUIDAuditBase):
    """A tag for categorizing resources."""

    name: str | None = field(default=None, validator=validators.max_len(100))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))

    @classmethod
    def unique_hash(cls, name: str, slug: str | None = None) -> Hashable:
        return slugify(name)


# SQLAlchemy Imperative Mapping

tag = Table(
    "tag",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
)

# Add slug column and constraints
add_slug_column(tag)


mapper.map_imperatively(
    Tag,
    tag,
    properties={
        "groups": relationship(
            "Group",
            secondary=lambda: _team_tag(),
            back_populates="tags",
        )
    },
)


def _team_tag() -> Table:
    from leaguemanager.models.account.group_tag import group_tag

    return group_tag
