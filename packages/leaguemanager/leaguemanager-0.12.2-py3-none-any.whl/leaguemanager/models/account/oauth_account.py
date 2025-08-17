from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

if TYPE_CHECKING:
    from .role import Role
    from .user import User


@define(slots=False)
class UserOauthAccount(UUIDAuditBase):
    """A user OAuth account."""

    user_id: UUID = field(default=None)
    oauth_name: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))
    access_token: str | None = field(default=None)
    expires_at: int | None = field(default=None)
    refresh_token: str | None = field(default=None)
    account_id: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    account_email: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    token_expires_at: datetime | None = field(default=None)
    scope: str | None = field(default=None)
    provider_user_data: dict | None = field(default=None)
    last_login_at: datetime | None = field(default=None)

    # Association Proxies
    user_name: str | None = None
    user_email: str | None = None


# SQLAlchemy Imperative Mappings

user_oauth = Table(
    "user_oauth",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("user_id", SA_UUID, ForeignKey("user_account.id"), nullable=False),
    Column("oauth_name", String(100), nullable=True, index=True),
    Column("access_token", Text, nullable=False),
    Column("expires_at", Integer, nullable=True),
    Column("refresh_token", Text, nullable=True),
    Column("account_id", String(255), nullable=False, index=True),
    Column("account_email", String(255), nullable=False),
    Column("token_expires_at", DateTime, nullable=True),
    Column("scope", Text, nullable=True),
    Column("provider_user_data", JSON, nullable=True),
    Column("last_login_at", DateTime, nullable=True),
)

# ORM Relationships

mapper.map_imperatively(
    UserOauthAccount,
    user_oauth,
    properties={
        "user": relationship(
            "User",
            back_populates="oauth_accounts",
            viewonly=True,
            innerjoin=True,
            lazy="joined",
        ),
    },
)

UserOauthAccount.user_name = association_proxy("user", "username")
UserOauthAccount.user_email = association_proxy("user", "email")
