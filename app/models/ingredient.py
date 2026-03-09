"""
app/models/ingredient.py

Defines the Ingredient ORM model.

Each Ingredient belongs to exactly one Recipe and stores
the item name, quantity, and unit of measurement.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class Ingredient(Base):
    """
    Represents a single ingredient within a recipe.

    Attributes:
        id:        Auto-incremented primary key.
        recipe_id: Foreign key pointing to the parent Recipe.
        name:      Ingredient name (e.g. "flour", "eggs").
        amount:    Numeric quantity (e.g. 250).
        unit:      Unit of measurement (e.g. "g", "ml", "pcs").
        recipe:    Back-reference to the parent Recipe object.
    """

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False, default="")

    recipe = relationship("Recipe", back_populates="ingredients")

    def __repr__(self) -> str:
        return (
            f"<Ingredient id={self.id} name='{self.name}' "
            f"amount={self.amount} {self.unit}>"
        )
