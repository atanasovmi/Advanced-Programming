"""Defines the Milestone ORM model for venture roadmaps."""

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Milestone(Base):
    """Represents one ordered roadmap milestone in a venture brief."""

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    venture_id = Column(Integer, ForeignKey("ventures.id"), nullable=False)
    number = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=False, default="")

    venture = relationship("Venture", back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Milestone id={self.id} number={self.number}>"
