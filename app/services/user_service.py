"""Contains business logic related to user accounts and shortlists."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.shortlist import Shortlist
from app.models.user import User
from app.models.venture import Venture


class UserService:
    """Provides registration, authentication, profile, and shortlist operations."""

    @staticmethod
    def register(
        db: Session,
        username: str,
        email: str,
        password: str,
        bio: str = "",
    ) -> User:
        """Create and persist a new user account."""
        username = username.strip()
        email = email.strip().lower()
        bio = bio.strip()

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(username) > 80:
            raise ValueError("Username must not exceed 80 characters.")
        if not all(c.isalnum() or c == "_" for c in username):
            raise ValueError(
                "Username may only contain letters, digits, and underscores."
            )
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please enter a valid email address.")

        if db.query(User).filter(User.username == username).first():
            raise ValueError(f"The username '{username}' is already taken.")
        if db.query(User).filter(User.email == email).first():
            raise ValueError("An account with this email address already exists.")

        user = User(
            username=username,
            email=email,
            password_hash=User.hash_password(password),
            bio=bio,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """Return the user if credentials are valid, else None."""
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return None
        if not User.verify_password(user.password_hash, password):
            return None
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Return the user with the given primary key, or None."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Return the user with the given username, or None."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_bio(db: Session, user_id: int, bio: str) -> Optional[User]:
        """Update the bio text for the given user."""
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None
        user.bio = bio.strip()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def add_shortlist(db: Session, user_id: int, venture_id: int) -> Shortlist:
        """Add a venture brief to a user's shortlist."""
        if not db.query(User).filter(User.id == user_id).first():
            raise ValueError("User not found.")
        if not db.query(Venture).filter(Venture.id == venture_id).first():
            raise ValueError("Venture not found.")

        existing = (
            db.query(Shortlist)
            .filter(Shortlist.user_id == user_id, Shortlist.venture_id == venture_id)
            .first()
        )
        if existing:
            return existing

        shortlist = Shortlist(user_id=user_id, venture_id=venture_id)
        db.add(shortlist)
        db.commit()
        db.refresh(shortlist)
        return shortlist

    @staticmethod
    def remove_shortlist(db: Session, user_id: int, venture_id: int) -> bool:
        """Remove a venture brief from a user's shortlist."""
        shortlist = (
            db.query(Shortlist)
            .filter(Shortlist.user_id == user_id, Shortlist.venture_id == venture_id)
            .first()
        )
        if shortlist is None:
            return False
        db.delete(shortlist)
        db.commit()
        return True

    @staticmethod
    def is_shortlisted(db: Session, user_id: int, venture_id: int) -> bool:
        """Return True when the venture is already on the user's shortlist."""
        return (
            db.query(Shortlist)
            .filter(Shortlist.user_id == user_id, Shortlist.venture_id == venture_id)
            .first()
        ) is not None

    @staticmethod
    def get_shortlisted_ventures(db: Session, user_id: int) -> list[Venture]:
        """Return all shortlisted ventures for a user, newest first."""
        shortlists = (
            db.query(Shortlist)
            .filter(Shortlist.user_id == user_id)
            .order_by(Shortlist.created_at.desc())
            .all()
        )
        return [shortlist.venture for shortlist in shortlists if shortlist.venture is not None]
