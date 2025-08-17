from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import ModelDictT, is_dict, schema_dump
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.lib.exceptions import HTTPException, PermissionDenied
from leaguemanager.lib.security import crypt
from leaguemanager.lib.settings import get_settings
from leaguemanager.lib.validation import PasswordValidationError, validate_password_strength
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

if TYPE_CHECKING:
    from uuid import UUID


__all__ = [
    "EmailVerificationService",
    "EmailVerificationAsyncService",
]

settings = get_settings()


class EmailVerificationService(SQLAlchemySyncRepositoryService):
    """Handles email verification operations."""

    class Repo(SQLAlchemySyncRepository[m.EmailVerificationToken]):
        """Email verification repository."""

        model_type = m.EmailVerificationToken

    repository_type = Repo


class EmailVerificationAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles email verification operations asynchronously."""

    class Repo(SQLAlchemyAsyncRepository[m.EmailVerificationToken]):
        """Email verification repository."""

        model_type = m.EmailVerificationToken

    repository_type = Repo
    match_fields = ["token"]

    async def create_verification_token(self, user_id: UUID, email: str) -> m.EmailVerificationToken:
        """Create a new email verification token for a user.

        Args:
            user_id: The user's UUID
            email: The email address to verify

        Returns:
            The created EmailVerificationToken instance
        """
        # Invalidate any existing tokens for this user/email combination
        await self.invalidate_user_tokens(user_id, email)

        # Generate a secure random token
        token = secrets.token_urlsafe(32)

        # Create token with 24-hour expiration
        verification_token = m.EmailVerificationToken(
            user_id=user_id, token=token, email=email, expires_at=m.EmailVerificationToken.create_expires_at(hours=24)
        )

        obj = await self.create(verification_token)
        return self.to_schema(obj)

    async def verify_token(self, token: str) -> m.EmailVerificationToken:
        """Verify a token and mark it as used.

        Args:
            token: The verification token string

        Returns:
            The EmailVerificationToken instance if valid

        Raises:
            HTTPException: If token is invalid, expired, or already used
        """
        verification_token = await self.repository.get_one_or_none(token=token)

        if verification_token is None:
            raise HTTPException(detail="Invalid verification token", status_code=400)

        if verification_token.is_expired:
            raise HTTPException(detail="Verification token has expired", status_code=400)

        if verification_token.is_used:
            raise HTTPException(detail="Verification token has already been used", status_code=400)

        # Mark token as used
        verification_token.used_at = datetime.now(UTC)
        obj = await self.update(verification_token)

        return self.to_schema(obj)

    async def invalidate_user_tokens(self, user_id: UUID, email: str | None = None) -> None:
        """Invalidate all tokens for a user, optionally filtered by email.

        Args:
            user_id: The user's UUID
            email: Optional email to filter tokens
        """
        filters = [m.EmailVerificationToken.user_id == user_id]
        if email:
            filters.append(m.EmailVerificationToken.email == email)

        # Find all active tokens
        tokens = await self.repository.list(*filters)

        # Mark them as used (invalidated)
        current_time = datetime.now(UTC)
        for token in tokens:
            if not token.is_used:
                token.used_at = current_time

        if tokens:
            await self.repository.update_many(tokens)

    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from the database.

        Returns:
            Number of tokens removed
        """
        current_time = datetime.now(UTC)
        expired_tokens = await self.repository.list(m.EmailVerificationToken.expires_at < current_time)

        if expired_tokens:
            await self.repository.delete_many(expired_tokens)

        return len(expired_tokens)
