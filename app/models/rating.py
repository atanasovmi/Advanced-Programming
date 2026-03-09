"""
app/models/rating.py

Defines the Rating ORM model.

Users can leave a star rating (1–5) and an optional comment
for any recipe. Multiple ratings per recipe are allowed.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.database import Base


class Rating(Base):
    """
    Represents a user rating for a recipe.

    Attributes:
        id:         Auto-incremented primary key.
        recipe_id:  Foreign key pointing to the rated Recipe.
        score:      Star rating between 1 and 5 (inclusive).
        comment:    Optional free-text feedback.
        created_at: Timestamp set automatically on creation.
        recipe:     Back-reference to the parent Recipe object.
    """

    __tablename__ = "ratings"

    # Database-level constraint ensures score is always 1–5.
    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False, default="")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    recipe = relationship("Recipe", back_populates="ratings")

    def __repr__(self) -> str:
        return f"<Rating id={self.id} score={self.score}>"
