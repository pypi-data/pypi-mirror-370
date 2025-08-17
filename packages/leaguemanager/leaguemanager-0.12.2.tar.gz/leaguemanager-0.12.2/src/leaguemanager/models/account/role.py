from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, String, Table
from sqlalchemy.orm import relationship

from leaguemanager.models.base import UUIDBase, add_slug_column, mapper, metadata


@define(slots=False)
class Role(UUIDBase):
    """A role defining permissions in the system."""

    name: str | None = field(default=None, validator=validators.max_len(24))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))


# SQLAlchemy Imperative Mapping

role = Table(
    "role",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("name", String(24), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
)

# Add slug column and constraints
add_slug_column(role)

# ORM Relationships

mapper.map_imperatively(
    Role,
    role,
    properties={
        "user_roles": relationship(
            "UserRole",
            back_populates="role",
            lazy="noload",
            viewonly=True,
            cascade="all, delete",
        )
    },
)
