from __future__ import annotations

from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.account.email_verification_token import EmailVerificationToken

# from leaguemanager.models.account.oauth_account import UserOauthAccount
from leaguemanager.models.base import IndividualBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from .email_verification_token import EmailVerificationToken
    from .group import Group
    from .user_role import UserRole


@define(slots=False)
class User(IndividualBase):
    """A user of the system."""

    username: str | None = field(default=None, validator=validators.optional(validators.max_len(40)))
    email: str | None = field(default=None, validator=validators.max_len(40))
    hashed_password: str | None = field(default=None, validator=validators.max_len(32))
    active: bool = field(default=True)
    superuser: bool = field(default=False)
    verified: bool = field(default=False)
    verified_at: datetime | None = field(default=None)
    joined: datetime | None = field(factory=lambda: datetime.now(UTC))

    # Password reset fields
    password_reset_at: datetime | None = field(default=None)
    failed_reset_attempts: int = field(default=0)
    reset_locked_until: datetime | None = field(default=None)

    @classmethod
    def signup(cls, email: str) -> "User":
        return cls(
            username=email,
            email=email,
            hashed_password="",
            active=True,
            superuser=False,
        )


# SQLAlchemy Imperative Mapping

user_account = Table(
    "user_account",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("username", String(40), unique=True, nullable=True, index=True),
    Column("email", String(40), unique=True, nullable=False),
    Column("hashed_password", String(255), nullable=True),
    Column("active", Boolean, default=True),
    Column("superuser", Boolean, default=False),
    Column("verified", Boolean, default=False),
    Column("verified_at", DateTime, default=None),
    Column("joined", DateTime, default=lambda: datetime.now(UTC)),
    Column("password_reset_at", DateTime, default=None, nullable=True),
    Column("failed_reset_attempts", Integer, default=0, nullable=False),
    Column("reset_locked_until", DateTime, default=None, nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    User,
    user_account,
    properties={
        "groups": relationship(
            "GroupMember",
            back_populates="user",
            uselist=True,
            lazy="selectin",
            cascade="all, delete",
            viewonly=True,
        ),
        "user_roles": relationship(
            "UserRole",
            back_populates="user",
            lazy="selectin",
            cascade="all, delete",
            uselist=True,
        ),
        "verification_tokens": relationship(
            "EmailVerificationToken",
            back_populates="user",
            lazy="noload",
            cascade="all, delete",
            uselist=True,
        ),
        "oauth_accounts": relationship(
            "UserOauthAccount",
            back_populates="user",
            lazy="noload",
            cascade="all, delete",
            uselist=True,
        ),
        "reset_tokens": relationship(
            "PasswordResetToken",
            back_populates="user",
            lazy="noload",
            cascade="all, delete",
            uselist=True,
        ),
    },
)
