"""
app/services/__init__.py

Exports the service classes so consumers only need one import path.
"""

from app.services.recipe_service import RecipeService
from app.services.rating_service import RatingService

__all__ = ["RecipeService", "RatingService"]
