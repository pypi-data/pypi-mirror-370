from __future__ import annotations  # noqa: A005

import asyncio
import base64
import secrets

import attrs
from passlib.context import CryptContext

from leaguemanager.lib.settings import get_settings

settings = get_settings()

__all__ = ["Crypt", "crypt"]


@attrs.define
class Crypt:
    """Cryptography utilities for password hashing and verification."""

    schemes: list[str] = attrs.field(default=settings.security.crypt_schemes)
    crypt_context: CryptContext = attrs.field(init=False)

    def __attrs_post_init__(self):
        """Post-initialization to set up the password hashing context."""
        # Ensure that the 'argon2-cffi' package is installed for this to work.

        if not self.schemes:
            self.schemes = ["argon2"]
        self.crypt_context = CryptContext(schemes=self.schemes, deprecated="auto")

    def generate_password(self, length: int = 16) -> str:
        """Generate a random password.

        Args:
            length (int): Length of the password to generate. Default is 16.

        Returns:
            str: Randomly generated password.
        """
        return secrets.token_urlsafe(length)

    def get_encryption_key(secret: str) -> bytes:
        """Get encryption key.

        Args:
            secret (str): Secret key used for encryption

        Returns:
            bytes: a URL safe encoded version of secret
        """
        if len(secret) <= 32:
            secret = f"{secret:<32}"[:32]
        return base64.urlsafe_b64encode(secret.encode())

    async def get_password_hash(self, password: str | bytes) -> str:
        """Get password hash.

        Args:
            password: Plain password
        Returns:
            str: Hashed password
        """
        return await asyncio.get_running_loop().run_in_executor(None, self.crypt_context.hash, password)

    async def verify_password(self, plain_password: str | bytes, hashed_password: str) -> bool:
        """Verify Password.

        Args:
            plain_password (str | bytes): The string or byte password
            hashed_password (str): the hash of the password

        Returns:
            bool: True if password matches hash.
        """
        valid, _ = await asyncio.get_running_loop().run_in_executor(
            None,
            self.crypt_context.verify_and_update,
            plain_password,
            hashed_password,
        )
        return bool(valid)


crypt = Crypt()
