"""
app/models/recipe.py

Defines the Recipe ORM model and the Category enum.

A Recipe is the central entity of the application.
It owns a list of Ingredients, ordered Steps, and user Ratings.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class Category(str, enum.Enum):
    """Food categories used to classify recipes."""

    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    DESSERT = "Dessert"
    SNACK = "Snack"
    DRINK = "Drink"


class Recipe(Base):
    """
    Represents a single recipe entry in the database.

    Attributes:
        id:          Auto-incremented primary key.
        title:       Name of the recipe (must be unique).
        description: Short teaser text shown on the recipe cards.
        category:    One of the Category enum values.
        servings:    How many portions the recipe yields.
        prep_time:   Preparation time in minutes.
        cook_time:   Cooking / baking time in minutes.
        created_at:  Timestamp set automatically when the record is created.
        ingredients: Related Ingredient objects (one-to-many).
        steps:       Related Step objects (one-to-many, ordered).
        ratings:     Related Rating objects (one-to-many).
    """

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=False, default="")
    category = Column(Enum(Category), nullable=False, default=Category.DINNER)
    servings = Column(Integer, nullable=False, default=2)
    prep_time = Column(Integer, nullable=False, default=0)   # minutes
    cook_time = Column(Integer, nullable=False, default=0)   # minutes
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    # Optional link to the user who created this recipe.
    # NULL means the recipe was added anonymously / seeded.
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    author = relationship("User", back_populates="recipes")

    # Cascade delete: when a recipe is deleted, its children are too.
    ingredients = relationship(
        "Ingredient", back_populates="recipe",
        cascade="all, delete-orphan", order_by="Ingredient.id"
    )
    steps = relationship(
        "Step", back_populates="recipe",
        cascade="all, delete-orphan", order_by="Step.number"
    )
    ratings = relationship(
        "Rating", back_populates="recipe",
        cascade="all, delete-orphan", order_by="Rating.created_at"
    )
    bookmarks = relationship(
        "Bookmark", back_populates="recipe",
        cascade="all, delete-orphan"
    )

    @property
    def total_time(self) -> int:
        """Return the combined prep + cook time in minutes."""
        return self.prep_time + self.cook_time

    @property
    def average_rating(self) -> float:
        """
        Calculate the average star rating across all submitted ratings.

        Returns 0.0 when no ratings have been submitted yet.
        """
        if not self.ratings:
            return 0.0
        return sum(r.score for r in self.ratings) / len(self.ratings)

    def __repr__(self) -> str:
        return f"<Recipe id={self.id} title='{self.title}'>"
