"""
app/models/venture.py

Defines the Venture ORM model and the Sector enum.

A Venture is the central entity of VentureCanvas. It stores a short
innovation brief together with the capability needs, roadmap milestones,
and peer reviews that belong to it.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Sector(str, enum.Enum):
    """Strategic sectors used to classify venture briefs."""

    AI_DATA = "AI & Data"
    SUSTAINABILITY = "Sustainability"
    HEALTH = "Health"
    EDUCATION = "Education"
    CULTURE = "Culture"
    PRODUCTIVITY = "Productivity"


class Venture(Base):
    """Represents one innovation venture brief."""

    __tablename__ = "ventures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=False, default="")
    sector = Column(Enum(Sector), nullable=False, default=Sector.PRODUCTIVITY)
    team_size = Column(Integer, nullable=False, default=3)
    discovery_weeks = Column(Integer, nullable=False, default=0)
    build_weeks = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    author = relationship("User", back_populates="ventures")
    resource_needs = relationship(
        "ResourceNeed",
        back_populates="venture",
        cascade="all, delete-orphan",
        order_by="ResourceNeed.id",
    )
    milestones = relationship(
        "Milestone",
        back_populates="venture",
        cascade="all, delete-orphan",
        order_by="Milestone.number",
    )
    reviews = relationship(
        "Review",
        back_populates="venture",
        cascade="all, delete-orphan",
        order_by="Review.created_at",
    )
    shortlists = relationship(
        "Shortlist",
        back_populates="venture",
        cascade="all, delete-orphan",
    )

    @property
    def timeline_weeks(self) -> int:
        """Return the combined discovery and build effort in weeks."""
        return self.discovery_weeks + self.build_weeks

    @property
    def average_score(self) -> float:
        """Return the mean peer review score, or 0.0 when there are none."""
        if not self.reviews:
            return 0.0
        return sum(review.score for review in self.reviews) / len(self.reviews)

    def __repr__(self) -> str:
        return f"<Venture id={self.id} title='{self.title}'>"
