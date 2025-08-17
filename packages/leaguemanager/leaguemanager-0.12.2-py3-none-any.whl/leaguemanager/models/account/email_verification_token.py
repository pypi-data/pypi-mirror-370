from datetime import UTC, datetime, timedelta
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
class EmailVerificationToken(UUIDAuditBase):
    """A user email verification token."""

    user_id: UUID = field(default=None)
    token: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    email: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    expires_at: datetime | None = field(default=None)
    used_at: datetime | None = field(default=None)

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now(UTC) > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if the token has been used."""
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if the token is valid (not expired and not used)."""
        return not self.is_expired and not self.is_used

    @classmethod
    def create_expires_at(cls, hours: int = 24) -> datetime:
        """Create an expiration datetime for the token.

        Returns:
            datetime: The expiration datetime set to the current time plus the specified hours.
        """
        return datetime.now(UTC) + timedelta(hours=hours)


# SQLAlchemy Imperative Mappings

email_verification_token = Table(
    "email_verification_token",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("user_id", SA_UUID, ForeignKey("user_account.id"), nullable=False),
    Column("token", String(255), nullable=True),
    Column("email", String(255), nullable=True),
    Column("expires_at", DateTime(timezone=True), nullable=True),
    Column("used_at", DateTime(timezone=True), nullable=True),
)

# ORM Relationships

mapper.map_imperatively(
    EmailVerificationToken,
    email_verification_token,
    properties={
        "user": relationship("User", back_populates="verification_tokens", lazy="selectin"),
    },
)
