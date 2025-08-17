from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDBase, mapper, metadata

if TYPE_CHECKING:
    from .role import Role
    from .user import User


@define(slots=False)
class UserRole(UUIDBase):
    """A relationship link between a user and a role."""

    user_id: UUID | None = field(default=None)
    role_id: UUID | None = field(default=None)
    assigned_at: datetime = field(factory=lambda: datetime.now(UTC))

    # Association Proxies
    role_name: str | None = None
    role_slug: str | None = None
    username: str | None = None
    user_email: str | None = None


# SQLAlchemy Imperative Mapping

user_role = Table(
    "user_role",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("user_id", SA_UUID, ForeignKey("user_account.id"), primary_key=True),
    Column("role_id", SA_UUID, ForeignKey("role.id"), primary_key=True),
    Column("assigned_at", DateTime, nullable=False),
)

# ORM Relationships

mapper.map_imperatively(
    UserRole,
    user_role,
    properties={
        "user": relationship("User", back_populates="user_roles"),
        "role": relationship("Role", back_populates="user_roles"),
    },
)


UserRole.role_name = association_proxy("role", "name")
UserRole.role_slug = association_proxy("role", "slug")
UserRole.username = association_proxy("user", "username")
UserRole.user_email = association_proxy("user", "email")
