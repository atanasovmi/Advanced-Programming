"""
app/views/__init__.py

Registers all NiceGUI page routes.
Importing this module is enough to activate every route.
"""

from app.views import home, recipe_detail, add_recipe, shopping_list  # noqa: F401
from app.views import auth, profile  # noqa: F401

__all__ = ["home", "recipe_detail", "add_recipe", "shopping_list", "auth", "profile"]
