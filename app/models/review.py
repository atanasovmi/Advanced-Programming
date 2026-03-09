"""Defines the Review ORM model for peer feedback on ventures."""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Review(Base):
    """Represents one peer review score and optional comment."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="ck_review_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    venture_id = Column(Integer, ForeignKey("ventures.id"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False, default="")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    venture = relationship("Venture", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review id={self.id} score={self.score}>"
