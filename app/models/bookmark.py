"""
app/models/bookmark.py

Defines the Bookmark ORM model.

A Bookmark represents a User saving a Recipe to their personal
collection. The combination of (user_id, recipe_id) is unique so a
user cannot bookmark the same recipe twice.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.database import Base


class Bookmark(Base):
    """
    Join table that links a User to a bookmarked Recipe.

    Attributes:
        id:         Auto-incremented primary key.
        user_id:    FK → users.id
        recipe_id:  FK → recipes.id
        created_at: Timestamp set when the bookmark is created.
        user:       Back-reference to the owning User.
        recipe:     Back-reference to the bookmarked Recipe.
    """

    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id",   ondelete="CASCADE"), nullable=False)
    recipe_id  = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    user   = relationship("User",   back_populates="bookmarks")
    recipe = relationship("Recipe", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark user_id={self.user_id} recipe_id={self.recipe_id}>"
