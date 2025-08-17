from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.orm import relationship

from leaguemanager.models.base import UUIDAuditBase, add_slug_column, mapper, metadata
from leaguemanager.models.enums import GroupRole


def group_type_converter(value):
    if isinstance(value, GroupRole):
        return value.name
    return value


@define(slots=False)
class GroupInvitation(UUIDAuditBase):
    """An invite to a group."""

    group_id: UUID | None = field(default=None)
    email: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    group_role: str | None = field(
        default=None,
        converter=group_type_converter,
        validator=validators.optional(validators.in_({e.name for e in GroupRole})),
    )
    is_accepted: bool = field(default=False)
    invited_by_id: UUID | None = field(default=None)
    invited_by_email: str | None = field(default=None)

    # ORM Relationship


group_invitation = Table(
    "group_invitation",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("group_id", SA_UUID, ForeignKey("group.id", ondelete="cascade"), nullable=False),
    Column(
        "email",
        String(255),
        nullable=True,
    ),
    Column("group_role", SA_Enum(GroupRole), default=(GroupRole.MEMBER)),
    Column("is_accepted", Boolean, default=False),
    Column("invited_by_id", SA_UUID, ForeignKey("user_account.id", ondelete="set null"), nullable=True),
    Column("invited_by_email", String, nullable=True),
)

# ORM Relationships

mapper.map_imperatively(
    GroupInvitation,
    group_invitation,
    properties={
        "group": relationship(
            "Group",
            foreign_keys="GroupInvitation.group_id",
            innerjoin=True,
            viewonly=True,
        ),
        "invited_by": relationship(
            "User",
            foreign_keys="GroupInvitation.invited_by_id",
            uselist=False,
            viewonly=True,
        ),
    },
)
