"""
app/services/user_service.py

Contains all business logic related to user accounts.

The UserService class manages registration, authentication, and
profile retrieval. It never touches the database directly in views;
all calls go through this service.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.recipe import Recipe


class UserService:
    """
    Provides user account operations: registration, authentication,
    profile lookups, and bookmark management.

    All methods accept a SQLAlchemy Session as their first argument
    so that the caller controls the transaction scope.
    """

    # ------------------------------------------------------------------
    # Registration & authentication
    # ------------------------------------------------------------------

    @staticmethod
    def register(
        db: Session,
        username: str,
        email: str,
        password: str,
        bio: str = "",
    ) -> User:
        """
        Create a new user account.

        Args:
            db:       Active database session.
            username: Unique display name (3–80 characters, alphanumeric +
                      underscores only).
            email:    Unique email address.
            password: Plain-text password (min 6 characters).
            bio:      Optional short self-description.

        Returns:
            The newly created and committed User object.

        Raises:
            ValueError: If any validation rule is violated or the
                        username / email is already taken.
        """
        username = username.strip()
        email    = email.strip().lower()
        bio      = bio.strip()

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
        """
        Return the User if *username* + *password* are valid, else None.

        Args:
            db:       Active database session.
            username: The user's display name (case-sensitive).
            password: Plain-text password to verify.
        """
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return None
        if not User.verify_password(user.password_hash, password):
            return None
        return user

    # ------------------------------------------------------------------
    # Profile lookups
    # ------------------------------------------------------------------

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
        """
        Update the bio text for the given user.

        Returns:
            The updated User, or None if no such user exists.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None
        user.bio = bio.strip()
        db.commit()
        db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # Bookmark management
    # ------------------------------------------------------------------

    @staticmethod
    def add_bookmark(db: Session, user_id: int, recipe_id: int) -> Bookmark:
        """
        Bookmark *recipe_id* for *user_id*.

        Returns:
            The new (or existing) Bookmark object.

        Raises:
            ValueError: If either the user or recipe does not exist.
        """
        if not db.query(User).filter(User.id == user_id).first():
            raise ValueError("User not found.")
        if not db.query(Recipe).filter(Recipe.id == recipe_id).first():
            raise ValueError("Recipe not found.")

        existing = (
            db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.recipe_id == recipe_id)
            .first()
        )
        if existing:
            return existing

        bm = Bookmark(user_id=user_id, recipe_id=recipe_id)
        db.add(bm)
        db.commit()
        db.refresh(bm)
        return bm

    @staticmethod
    def remove_bookmark(db: Session, user_id: int, recipe_id: int) -> bool:
        """
        Remove the bookmark for *recipe_id* from *user_id*'s collection.

        Returns:
            True if a bookmark was removed, False if none existed.
        """
        bm = (
            db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.recipe_id == recipe_id)
            .first()
        )
        if bm is None:
            return False
        db.delete(bm)
        db.commit()
        return True

    @staticmethod
    def is_bookmarked(db: Session, user_id: int, recipe_id: int) -> bool:
        """Return True if the user has bookmarked the given recipe."""
        return (
            db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.recipe_id == recipe_id)
            .first()
        ) is not None

    @staticmethod
    def get_bookmarked_recipes(db: Session, user_id: int) -> list[Recipe]:
        """Return all recipes bookmarked by the user, newest first."""
        bookmarks = (
            db.query(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
            .all()
        )
        return [bm.recipe for bm in bookmarks if bm.recipe is not None]
