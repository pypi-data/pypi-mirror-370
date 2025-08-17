from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.lib.exceptions import HTTPException, PermissionDenied
from leaguemanager.lib.security import crypt
from leaguemanager.lib.settings import get_settings
from leaguemanager.lib.validation import PasswordValidationError, validate_password_strength
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

if TYPE_CHECKING:
    from uuid import UUID

    from httpx_oauth.oauth2 import OAuth2Token

__all__ = [
    "UserSyncService",
    "UserAsyncService",
]

settings = get_settings()
MAX_FAILED_RESET_ATTEMPTS = 5


class UserSyncService(SQLAlchemySyncRepositoryService):
    """Handles user database operations."""

    class Repo(SQLAlchemySyncRepository[m.User]):
        """User repository."""

        model_type = m.User

    repository_type = Repo


class UserAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles user database operations."""

    class Repo(SQLAlchemyAsyncRepository[m.User]):
        """User repository."""

        model_type = m.User
        default_role = settings.role.default_user
        match_fields = ["email"]

    repository_type = Repo

    async def authenticate(self, username: str, password: bytes | str) -> m.User:
        """Authenticate a user against the stored hashed password.

        Returns:
            The user object if authentication is successful.

        Raises:
            PermissionDenied: If fails to locate, password is incorrect, or user inactive.
        """
        db_obj: m.User = await self.get_one_or_none(email=username)
        if not db_obj:
            raise PermissionDenied(detail="Invalid username or password")
        if not db_obj.hashed_password:
            raise PermissionDenied(detail="Invalid username or password")
        if not await crypt.verify_password(password, db_obj.hashed_password):
            raise PermissionDenied(detail="Invalid username or password")
        if not db_obj.active:
            raise PermissionDenied(detail="User is inactive")
        return db_obj

    async def verify_email(self, user_id: UUID, email: str) -> m.User:
        """Verify a user's email. Generally used for web app usage.

        Args:
            user_id (UUID): The ID of the user.
            email (str): The email to verify.

        Returns:
            m.User: The updated user object with verified email.
        """
        db_obj: m.User = await self.get_one_or_none(user_id)
        if not db_obj:
            raise HTTPException(detail="User not found", status_code=404)
        if db_obj.email != email:
            raise HTTPException(detail="Email does not match", status_code=400)
        db_obj.verified = True
        db_obj.verified_at = datetime.now(UTC).date()
        return await self.update(db_obj)

    async def require_verified_email(self, user: m.User) -> None:
        """Ensure the user has a verified email.

        Args:
            user (m.User): The user object to check.

        Raises:
            HTTPException: If the user's email is not verified.
        """
        if not user.verified:
            raise PermissionDenied(detail="Email not verified")

    async def update_password(self, data: dict[str | Any], user: m.User) -> m.User:
        """Update the user's password.

        Args:
            data (dict): The data containing the new password.
            user (m.User): The user object to update.

        Returns:
            m.User: The updated user object with the new password.
        """
        if user.hashed_password is None:
            raise PermissionDenied(detail="Invalid username or password")
        if not await crypt.verify_password(data["current_password"], user.hashed_password):
            raise PermissionDenied(detail="Invalid username or password")
        if not user.active:
            raise PermissionDenied(detail="User is inactive")
        user.hashed_password = await crypt.get_password_hash(data["new_password"])
        return await self.repository.update(user)

    @staticmethod
    async def has_role_id(db_obj: m.User, role_id: UUID) -> bool:
        """Return true if user has specified role ID"""
        return any(assigned_role.role_id for assigned_role in db_obj.user_roles if assigned_role.role_id == role_id)

    @staticmethod
    async def has_role(db_obj: m.User, role_name: str) -> bool:
        """Return true if user has specified role ID"""
        return any(assigned_role.role_id for assigned_role in db_obj.user_roles if assigned_role.role_name == role_name)

    @staticmethod
    def is_superuser(user: m.User) -> bool:
        return bool(
            user.superuser
            or any(
                assigned_role.role_name
                for assigned_role in user.roles
                if assigned_role.role_name == settings.role.superuser
            ),
        )

    async def reset_password_with_token(self, user_id: UUID, new_password: str) -> m.User:
        """Reset user's password using a validated token.

        Args:
            user_id: The user's UUID
            new_password: The new password

        Returns:
            The updated user object

        Raises:
            HTTPException: If user not found or password validation fails
        """
        # Validate password strength
        try:
            validate_password_strength(new_password)
        except PasswordValidationError as e:
            raise HTTPException(detail=str(e), status_code=400) from e

        db_obj = await self.get_one_or_none(id=user_id)
        if db_obj is None:
            raise HTTPException(detail="User not found", status_code=404)

        if not db_obj.active:
            raise HTTPException(detail="User account is inactive", status_code=403)

        # Update password and reset security fields
        db_obj.hashed_password = await crypt.get_password_hash(new_password)
        db_obj.password_reset_at = datetime.now(UTC)
        db_obj.failed_reset_attempts = 0
        db_obj.reset_locked_until = None

        return await self.repository.update(db_obj)

    async def increment_failed_reset_attempt(self, user_id: UUID) -> None:
        """Increment failed reset attempts counter.

        Args:
            user_id: The user's UUID
        """
        db_obj = await self.get_one_or_none(id=user_id)
        if db_obj is None:
            return

        db_obj.failed_reset_attempts += 1

        # Lock account after max failed attempts for 1 hour
        if db_obj.failed_reset_attempts >= MAX_FAILED_RESET_ATTEMPTS:
            db_obj.reset_locked_until = datetime.now(UTC).replace(hour=datetime.now(UTC).hour + 1)

        await self.repository.update(db_obj)

    async def create_user_from_oauth(
        self,
        oauth_data: dict[str, Any],
        provider: str,
        token_data: OAuth2Token,
    ) -> m.User:
        """Create new user from OAuth data.

        Args:
            oauth_data: User data from OAuth provider
            provider: OAuth provider name (e.g., 'google')
            token_data: OAuth token data

        Returns:
            The created user object
        """
        # Extract user info from OAuth data
        email = oauth_data.get("email", "")
        username = oauth_data.get("name", "")

        # If username not provided, use email as username
        if not username:
            username = email

        # Create user data
        user_data = {
            "email": email,
            "username": username,
            "verified": True,  # Email is verified by OAuth provider
            "verified_at": datetime.now(UTC).date(),
            "active": True,
        }

        # Create the user
        return await self.create(data=user_data)

    async def authenticate_or_create_oauth_user(
        self,
        provider: str,
        oauth_data: dict[str, Any],
        token_data: OAuth2Token,
    ) -> tuple[m.User, bool]:
        """Authenticate existing OAuth user or create new one.

        Args:
            provider: OAuth provider name
            oauth_data: User data from OAuth provider
            token_data: OAuth token data

        Returns:
            Tuple of (user, is_new_user)
        """
        from app.services._user_oauth_accounts import UserOAuthAccountService

        # Check if user exists by email
        email = oauth_data.get("email", "")
        existing_user = await self.get_one_or_none(email=email) if email else None

        if existing_user:
            # User exists, update OAuth account
            oauth_service = UserOAuthAccountService(session=self.repository.session)
            await oauth_service.create_or_update_oauth_account(
                user_id=existing_user.id,
                provider=provider,
                oauth_data=oauth_data,
                token_data=token_data,
            )
            return existing_user, False

        # Create new user
        new_user = await self.create_user_from_oauth(
            oauth_data=oauth_data,
            provider=provider,
            token_data=token_data,
        )

        # Create OAuth account for new user
        oauth_service = UserOAuthAccountService(session=self.repository.session)
        await oauth_service.create_or_update_oauth_account(
            user_id=new_user.id,
            provider=provider,
            oauth_data=oauth_data,
            token_data=token_data,
        )

        return new_user, True
