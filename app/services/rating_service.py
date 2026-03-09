"""
app/services/rating_service.py

Contains business logic for submitting and retrieving ratings.

Keeping rating logic separate from RecipeService makes both
classes easier to read and extend independently.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.rating import Rating


class RatingService:
    """
    Provides operations for creating and reading recipe ratings.
    """

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @staticmethod
    def get_for_recipe(db: Session, recipe_id: int) -> list[Rating]:
        """
        Return all ratings for the given recipe, newest first.

        Args:
            db:        Active database session.
            recipe_id: Primary key of the target recipe.
        """
        return (
            db.query(Rating)
            .filter(Rating.recipe_id == recipe_id)
            .order_by(Rating.created_at.desc())
            .all()
        )

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @staticmethod
    def submit(
        db: Session,
        recipe_id: int,
        score: int,
        comment: str = "",
    ) -> Rating:
        """
        Persist a new rating for a recipe.

        Args:
            db:        Active database session.
            recipe_id: Primary key of the recipe being rated.
            score:     Star count; must be between 1 and 5.
            comment:   Optional feedback text.

        Returns:
            The newly created and committed Rating object.

        Raises:
            ValueError: If *score* is outside the valid 1–5 range.
        """
        if not 1 <= score <= 5:
            raise ValueError(f"Score must be between 1 and 5, got {score}.")

        rating = Rating(
            recipe_id=recipe_id,
            score=score,
            comment=comment.strip(),
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating
