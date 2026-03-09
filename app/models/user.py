"""
app/models/user.py

Defines the User ORM model for authentication and profile management.

A User can author venture briefs, shortlist promising ideas, and share a
public profile page showing their contributions.
"""

import hashlib
import os
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class User(Base):
    """Represents a registered VentureCanvas user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), nullable=False, unique=True, index=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    bio = Column(Text, nullable=False, default="")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    ventures = relationship(
        "Venture",
        back_populates="author",
        cascade="all, delete-orphan",
        order_by="Venture.created_at.desc()",
    )
    shortlists = relationship(
        "Shortlist",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Shortlist.created_at.desc()",
    )

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash *plain* with PBKDF2-HMAC-SHA256 and a random 16-byte salt."""
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
        return f"{salt.hex()}:{key.hex()}"

    @staticmethod
    def verify_password(stored_hash: str, plain: str) -> bool:
        """Return True when *plain* matches the stored password hash."""
        try:
            salt_hex, key_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
            return key.hex() == key_hex
        except (ValueError, AttributeError):
            return False

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}'>"
