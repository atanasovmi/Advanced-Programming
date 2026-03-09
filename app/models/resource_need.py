"""Defines the ResourceNeed ORM model for venture capability planning."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class ResourceNeed(Base):
    """Represents one required capability or resource for a venture."""

    __tablename__ = "resource_needs"

    id = Column(Integer, primary_key=True, index=True)
    venture_id = Column(Integer, ForeignKey("ventures.id"), nullable=False)
    name = Column(String(200), nullable=False)
    effort = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False, default="")

    venture = relationship("Venture", back_populates="resource_needs")

    def __repr__(self) -> str:
        return (
            f"<ResourceNeed id={self.id} name='{self.name}' "
            f"effort={self.effort} {self.unit}>"
        )
