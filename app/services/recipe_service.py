"""
app/services/recipe_service.py

Contains all business logic related to recipes.

The RecipeService class acts as the intermediary between the
presentation layer (NiceGUI views) and the persistence layer
(SQLAlchemy models). Views never touch the database directly;
they always go through a service method.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from app.models.recipe import Recipe, Category
from app.models.ingredient import Ingredient
from app.models.step import Step


class RecipeService:
    """
    Provides CRUD operations and queries for Recipe objects.

    All methods accept a SQLAlchemy Session as their first argument
    so that the caller controls the transaction scope.
    """

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @staticmethod
    def get_all(db: Session) -> list[Recipe]:
        """Return all recipes ordered by creation date (newest first)."""
        return (
            db.query(Recipe)
            .order_by(Recipe.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
        """
        Return the recipe with the given primary key, or None.

        Args:
            db:        Active database session.
            recipe_id: Primary key of the recipe to fetch.
        """
        return db.query(Recipe).filter(Recipe.id == recipe_id).first()

    @staticmethod
    def get_by_category(db: Session, category: Category) -> list[Recipe]:
        """
        Return all recipes that belong to the specified category.

        Args:
            db:       Active database session.
            category: The Category enum value to filter by.
        """
        return (
            db.query(Recipe)
            .filter(Recipe.category == category)
            .order_by(Recipe.created_at.desc())
            .all()
        )

    @staticmethod
    def search(db: Session, query: str) -> list[Recipe]:
        """
        Return all recipes whose title or description contains *query*
        (case-insensitive substring match).

        Args:
            db:    Active database session.
            query: Text fragment to look for.
        """
        like_pattern = f"%{query.lower()}%"
        return (
            db.query(Recipe)
            .filter(
                Recipe.title.ilike(like_pattern)
                | Recipe.description.ilike(like_pattern)
            )
            .order_by(Recipe.created_at.desc())
            .all()
        )

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        db: Session,
        title: str,
        description: str,
        category: Category,
        servings: int,
        prep_time: int,
        cook_time: int,
        ingredients: list[dict],
        steps: list[str],
    ) -> Recipe:
        """
        Persist a new recipe together with its ingredients and steps.

        Args:
            db:          Active database session.
            title:       Recipe name.
            description: Short description shown on the recipe card.
            category:    Category enum value.
            servings:    Number of portions.
            prep_time:   Preparation time in minutes.
            cook_time:   Cooking time in minutes.
            ingredients: List of dicts with keys "name", "amount", "unit".
            steps:       Ordered list of instruction strings.

        Returns:
            The newly created and committed Recipe object.

        Raises:
            ValueError: If *title* is empty or already taken.
        """
        title = title.strip()
        if not title:
            raise ValueError("Recipe title must not be empty.")

        existing = db.query(Recipe).filter(Recipe.title == title).first()
        if existing:
            raise ValueError(f"A recipe named '{title}' already exists.")

        recipe = Recipe(
            title=title,
            description=description.strip(),
            category=category,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
        )
        db.add(recipe)
        db.flush()  # Get the auto-generated recipe.id

        for item in ingredients:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=item["name"].strip(),
                amount=float(item.get("amount", 0)),
                unit=item.get("unit", "").strip(),
            )
            db.add(ingredient)

        for idx, text in enumerate(steps, start=1):
            step = Step(
                recipe_id=recipe.id,
                number=idx,
                description=text.strip(),
            )
            db.add(step)

        db.commit()
        db.refresh(recipe)
        return recipe

    @staticmethod
    def delete(db: Session, recipe_id: int) -> bool:
        """
        Delete a recipe and all its related data.

        Args:
            db:        Active database session.
            recipe_id: Primary key of the recipe to remove.

        Returns:
            True if the recipe was found and deleted, False otherwise.
        """
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe is None:
            return False
        db.delete(recipe)
        db.commit()
        return True
