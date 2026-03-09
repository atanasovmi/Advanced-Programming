"""
Unit tests for the service layer.

Validates UserService, RecipeService, and RatingService business logic.
"""

import pytest

from app.models.recipe import Category
from app.services.user_service import UserService
from app.services.recipe_service import RecipeService
from app.services.rating_service import RatingService


# ---------------------------------------------------------------------------
# UserService
# ---------------------------------------------------------------------------

class TestUserService:
    """Tests for user registration, authentication, and bookmarks."""

    def test_register_success(self, db):
        user = UserService.register(
            db, username="newuser", email="new@example.com",
            password="pass123", bio="Hi!",
        )
        assert user.id is not None
        assert user.username == "newuser"
        assert user.bio == "Hi!"

    def test_register_short_username(self, db):
        with pytest.raises(ValueError, match="at least 3 characters"):
            UserService.register(db, username="ab", email="a@b.com",
                                 password="pass123")

    def test_register_short_password(self, db):
        with pytest.raises(ValueError, match="at least 6 characters"):
            UserService.register(db, username="valid", email="a@b.com",
                                 password="12345")

    def test_register_invalid_email(self, db):
        with pytest.raises(ValueError, match="valid email"):
            UserService.register(db, username="valid", email="bademail",
                                 password="pass123")

    def test_register_duplicate_username(self, db):
        UserService.register(db, username="dup", email="a@b.com",
                             password="pass123")
        with pytest.raises(ValueError, match="already taken"):
            UserService.register(db, username="dup", email="b@c.com",
                                 password="pass123")

    def test_register_duplicate_email(self, db):
        UserService.register(db, username="user1", email="dup@x.com",
                             password="pass123")
        with pytest.raises(ValueError, match="already exists"):
            UserService.register(db, username="user2", email="dup@x.com",
                                 password="pass123")

    def test_authenticate_success(self, db):
        UserService.register(db, username="auth", email="a@a.com",
                             password="pass123")
        user = UserService.authenticate(db, "auth", "pass123")
        assert user is not None
        assert user.username == "auth"

    def test_authenticate_wrong_password(self, db):
        UserService.register(db, username="auth2", email="a2@a.com",
                             password="pass123")
        assert UserService.authenticate(db, "auth2", "wrong") is None

    def test_authenticate_unknown_user(self, db):
        assert UserService.authenticate(db, "ghost", "pw") is None

    def test_get_by_id_and_username(self, db):
        user = UserService.register(db, username="finder",
                                    email="f@x.com", password="pass123")
        assert UserService.get_by_id(db, user.id) is not None
        assert UserService.get_by_username(db, "finder") is not None
        assert UserService.get_by_id(db, 9999) is None
        assert UserService.get_by_username(db, "nope") is None

    def test_update_bio(self, db):
        user = UserService.register(db, username="biouser",
                                    email="b@x.com", password="pass123")
        updated = UserService.update_bio(db, user.id, "  New bio  ")
        assert updated.bio == "New bio"

    def test_bookmark_add_and_remove(self, db):
        user = UserService.register(db, username="bmuser",
                                    email="bm@x.com", password="pass123")
        recipe = RecipeService.create(
            db, title="BmRecipe", description="d", category=Category.SNACK,
            servings=1, prep_time=0, cook_time=0, ingredients=[], steps=[],
        )
        assert UserService.is_bookmarked(db, user.id, recipe.id) is False
        UserService.add_bookmark(db, user.id, recipe.id)
        assert UserService.is_bookmarked(db, user.id, recipe.id) is True

        # Adding the same bookmark again should be idempotent
        UserService.add_bookmark(db, user.id, recipe.id)
        assert UserService.is_bookmarked(db, user.id, recipe.id) is True

        UserService.remove_bookmark(db, user.id, recipe.id)
        assert UserService.is_bookmarked(db, user.id, recipe.id) is False

        # Removing non-existent bookmark returns False
        assert UserService.remove_bookmark(db, user.id, recipe.id) is False


# ---------------------------------------------------------------------------
# RecipeService
# ---------------------------------------------------------------------------

class TestRecipeService:
    """Tests for recipe CRUD and search."""

    def test_create_and_get(self, db):
        recipe = RecipeService.create(
            db, title="Pasta", description="Yummy",
            category=Category.DINNER, servings=2,
            prep_time=5, cook_time=15,
            ingredients=[{"name": "Noodles", "amount": 200, "unit": "g"}],
            steps=["Boil water", "Cook noodles"],
        )
        assert recipe.id is not None
        assert len(recipe.ingredients) == 1
        assert len(recipe.steps) == 2

        fetched = RecipeService.get_by_id(db, recipe.id)
        assert fetched.title == "Pasta"

    def test_create_empty_title_raises(self, db):
        with pytest.raises(ValueError, match="must not be empty"):
            RecipeService.create(
                db, title="", description="d", category=Category.LUNCH,
                servings=1, prep_time=0, cook_time=0,
                ingredients=[], steps=[],
            )

    def test_create_duplicate_title_raises(self, db):
        RecipeService.create(
            db, title="Unique", description="d", category=Category.LUNCH,
            servings=1, prep_time=0, cook_time=0,
            ingredients=[], steps=[],
        )
        with pytest.raises(ValueError, match="already exists"):
            RecipeService.create(
                db, title="Unique", description="d2",
                category=Category.LUNCH, servings=1, prep_time=0,
                cook_time=0, ingredients=[], steps=[],
            )

    def test_get_all_and_by_category(self, db):
        RecipeService.create(
            db, title="Cake", description="Sweet",
            category=Category.DESSERT, servings=4,
            prep_time=15, cook_time=30,
            ingredients=[], steps=[],
        )
        RecipeService.create(
            db, title="Soup", description="Warm",
            category=Category.LUNCH, servings=2,
            prep_time=5, cook_time=20,
            ingredients=[], steps=[],
        )
        assert len(RecipeService.get_all(db)) == 2
        assert len(RecipeService.get_by_category(db, Category.DESSERT)) == 1
        assert len(RecipeService.get_by_category(db, Category.BREAKFAST)) == 0

    def test_search(self, db):
        RecipeService.create(
            db, title="Banana Bread", description="Moist and easy",
            category=Category.DESSERT, servings=1,
            prep_time=10, cook_time=50,
            ingredients=[], steps=[],
        )
        assert len(RecipeService.search(db, "banana")) == 1
        assert len(RecipeService.search(db, "moist")) == 1
        assert len(RecipeService.search(db, "xyz")) == 0

    def test_delete(self, db):
        recipe = RecipeService.create(
            db, title="ToDelete", description="d",
            category=Category.SNACK, servings=1,
            prep_time=0, cook_time=0,
            ingredients=[], steps=[],
        )
        assert RecipeService.delete(db, recipe.id) is True
        assert RecipeService.get_by_id(db, recipe.id) is None
        assert RecipeService.delete(db, recipe.id) is False


# ---------------------------------------------------------------------------
# RatingService
# ---------------------------------------------------------------------------

class TestRatingService:
    """Tests for rating submission and retrieval."""

    def make_recipe(self, db):
        return RecipeService.create(
            db, title=f"R-{id(db)}", description="d",
            category=Category.DINNER, servings=1,
            prep_time=0, cook_time=0, ingredients=[], steps=[],
        )

    def test_submit_and_get(self, db):
        recipe = self.make_recipe(db)
        rating = RatingService.submit(db, recipe.id, score=4, comment="Great!")
        assert rating.id is not None
        assert rating.score == 4

        ratings = RatingService.get_for_recipe(db, recipe.id)
        assert len(ratings) == 1

    def test_submit_invalid_score(self, db):
        recipe = self.make_recipe(db)
        with pytest.raises(ValueError, match="between 1 and 5"):
            RatingService.submit(db, recipe.id, score=0)
        with pytest.raises(ValueError, match="between 1 and 5"):
            RatingService.submit(db, recipe.id, score=6)
