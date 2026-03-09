"""Defines the Shortlist ORM model for saved venture briefs."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.database import Base


class Shortlist(Base):
    """Join table that links a user to a saved venture brief."""

    __tablename__ = "shortlists"
    __table_args__ = (
        UniqueConstraint("user_id", "venture_id", name="uq_user_venture"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    venture_id = Column(Integer, ForeignKey("ventures.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    user = relationship("User", back_populates="shortlists")
    venture = relationship("Venture", back_populates="shortlists")

    def __repr__(self) -> str:
        return f"<Shortlist user_id={self.user_id} venture_id={self.venture_id}>"
