from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, String, Table
from sqlalchemy.orm import relationship

from leaguemanager.models.account.group_tag import group_tag
from leaguemanager.models.base import UUIDBase, add_slug_column, mapper, metadata


@define(slots=False)
class Group(UUIDBase):
    """A group of users with common permisions."""

    name: str | None = field(default=None, validator=validators.max_len(100))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(500)))
    active: bool = field(default=True)


# SQLAlchemy Imperative Mapping

group = Table(
    "group",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(500), nullable=True),
    Column("active", Boolean, default=True, nullable=False),
)


# ORM Relationships

mapper.map_imperatively(
    Group,
    group,
    properties={
        "members": relationship(
            "GroupMember",
            back_populates="group",
            lazy="selectin",
            passive_deletes=True,
            cascade="all, delete",
        ),
        "invitations": relationship(
            "GroupInvitation",
            back_populates="group",
            cascade="all, delete",
        ),
        "pending_invitations": relationship(
            "GroupInvitation",
            primaryjoin="and_(GroupInvitation.group_id==Group.id, GroupInvitation.is_accepted==False)",
            viewonly=True,
        ),
        "tags": relationship(
            "Tag",
            back_populates="groups",
            secondary=group_tag,
            cascade="all, delete",
            passive_deletes=True,
        ),
    },
)
