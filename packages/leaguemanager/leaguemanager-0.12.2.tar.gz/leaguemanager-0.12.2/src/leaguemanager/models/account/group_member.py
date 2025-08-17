from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata
from leaguemanager.models.enums import GroupRole

if TYPE_CHECKING:
    from .group import Group
    from .role import Role
    from .user import User


def group_type_converter(value):
    if isinstance(value, GroupRole):
        return value.name
    return value


@define(slots=False)
class GroupMember(UUIDAuditBase):
    """A relationship link between a user and a role."""

    user_id: UUID | None = field(default=None)
    group_id: UUID | None = field(default=None)
    group_role: str | None = field(
        default=None,
        converter=group_type_converter,
        validator=validators.optional(validators.in_({e.name for e in GroupRole})),
    )
    is_owner: bool = field(default=False)

    # Association Proxies
    username: str | None = None
    email: str | None = None
    team_name: str | None = None


# SQLAlchemy Imperative Mappings

group_member = Table(
    "group_member",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("user_id", SA_UUID, ForeignKey("user_account.id"), nullable=False),
    Column("group_id", SA_UUID, ForeignKey("group.id"), nullable=False),
    Column("group_role", SA_Enum(GroupRole), nullable=False, default=GroupRole.MEMBER, index=True),
    Column("is_owner", Boolean, default=False, nullable=False),
)


# ORM Relationships

mapper.map_imperatively(
    GroupMember,
    group_member,
    properties={
        "user": relationship(
            "User",
            back_populates="groups",
            foreign_keys="GroupMember.user_id",
            innerjoin=True,
            uselist=False,
            lazy="joined",
        ),
        "group": relationship(
            "Group",
            back_populates="members",
            foreign_keys="GroupMember.group_id",
            innerjoin=True,
            uselist=False,
            lazy="joined",
        ),
    },
)

GroupMember.username = association_proxy("user", "username")
GroupMember.email = association_proxy("user", "email")
GroupMember.team_name = association_proxy("group", "name")
