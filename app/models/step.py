"""
app/models/step.py

Defines the Step ORM model.

Each Step represents one numbered instruction within a recipe
(e.g. "Step 1: Preheat the oven to 200 °C").
"""

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class Step(Base):
    """
    Represents one numbered instruction step in a recipe.

    Attributes:
        id:          Auto-incremented primary key.
        recipe_id:   Foreign key pointing to the parent Recipe.
        number:      Step order (1, 2, 3 …).
        description: Full text of the instruction.
        recipe:      Back-reference to the parent Recipe object.
    """

    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    number = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=False, default="")

    recipe = relationship("Recipe", back_populates="steps")

    def __repr__(self) -> str:
        return f"<Step id={self.id} number={self.number}>"
