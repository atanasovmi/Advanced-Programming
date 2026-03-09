"""
app/models/user.py

Defines the User ORM model for authentication and profile management.

A User can author Recipes, bookmark Recipes they want to cook, and
has a public profile page showing their contributions.
"""

import hashlib
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base


class User(Base):
    """
    Represents a registered application user.

    Attributes:
        id:            Auto-incremented primary key.
        username:      Unique display name chosen at registration.
        email:         Unique email address used to identify the account.
        password_hash: PBKDF2-HMAC-SHA256 hash of the user's password
                       stored as "salt_hex:key_hex".
        bio:           Optional short self-description shown on the profile.
        created_at:    Timestamp set automatically when the record is created.
        recipes:       Recipes authored by this user (one-to-many).
        bookmarks:     Recipes this user has bookmarked (one-to-many).
    """

    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(80),  nullable=False, unique=True, index=True)
    email         = Column(String(200), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    bio           = Column(Text, nullable=False, default="")
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    recipes   = relationship(
        "Recipe",   back_populates="author",
        cascade="all, delete-orphan", order_by="Recipe.created_at.desc()"
    )
    bookmarks = relationship(
        "Bookmark", back_populates="user",
        cascade="all, delete-orphan", order_by="Bookmark.created_at.desc()"
    )

    # ------------------------------------------------------------------
    # Password helpers (stdlib only — no extra dependencies)
    # ------------------------------------------------------------------

    @staticmethod
    def hash_password(plain: str) -> str:
        """
        Hash *plain* with PBKDF2-HMAC-SHA256 and a random 16-byte salt.

        Returns:
            A string of the form ``<salt_hex>:<key_hex>`` suitable for
            storing in the ``password_hash`` column.
        """
        salt = os.urandom(16)
        # 260 000 iterations follows the OWASP 2023 recommendation for
        # PBKDF2-HMAC-SHA256 to make brute-force attacks computationally
        # expensive without noticeable latency for legitimate logins.
        key  = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
        return f"{salt.hex()}:{key.hex()}"

    @staticmethod
    def verify_password(stored_hash: str, plain: str) -> bool:
        """
        Return True if *plain* matches the *stored_hash*.

        Args:
            stored_hash: Value previously returned by :meth:`hash_password`.
            plain:       The plain-text password to check.
        """
        try:
            salt_hex, key_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            key  = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
            return key.hex() == key_hex
        except (ValueError, AttributeError):
            return False

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}'>"
