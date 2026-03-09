"""
Unit tests for ORM model classes.

Validates field defaults, computed properties, and password hashing.
"""

from app.models.user import User
from app.models.recipe import Recipe, Category
from app.models.ingredient import Ingredient
from app.models.step import Step
from app.models.rating import Rating
from app.models.bookmark import Bookmark


class TestUserModel:
    """Tests for the User model."""

    def test_hash_and_verify_password(self):
        """Hashed password should verify against the original plain text."""
        hashed = User.hash_password("secret123")
        assert User.verify_password(hashed, "secret123") is True

    def test_verify_wrong_password(self):
        """Wrong password should not verify."""
        hashed = User.hash_password("secret123")
        assert User.verify_password(hashed, "wrong") is False

    def test_verify_malformed_hash(self):
        """Malformed hash strings should return False, not raise."""
        assert User.verify_password("nocolon", "pw") is False
        assert User.verify_password("", "pw") is False
        assert User.verify_password(None, "pw") is False

    def test_user_repr(self, db):
        """__repr__ should include id and username."""
        user = User(username="tester", email="t@x.com",
                     password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.commit()
        assert "tester" in repr(user)

    def test_user_default_bio(self, db):
        """Bio should default to an empty string."""
        user = User(username="u1", email="u1@x.com",
                     password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.commit()
        assert user.bio == ""


class TestRecipeModel:
    """Tests for the Recipe model."""

    def test_total_time(self, db):
        """total_time should return prep_time + cook_time."""
        r = Recipe(title="Test", prep_time=10, cook_time=20,
                   category=Category.DINNER)
        db.add(r)
        db.commit()
        assert r.total_time == 30

    def test_average_rating_no_ratings(self, db):
        """average_rating should be 0.0 when there are no ratings."""
        r = Recipe(title="Empty", category=Category.LUNCH)
        db.add(r)
        db.commit()
        assert r.average_rating == 0.0

    def test_average_rating_with_ratings(self, db):
        """average_rating should compute correctly."""
        r = Recipe(title="Rated", category=Category.SNACK)
        db.add(r)
        db.flush()
        db.add_all([
            Rating(recipe_id=r.id, score=4),
            Rating(recipe_id=r.id, score=2),
        ])
        db.commit()
        db.refresh(r)
        assert r.average_rating == 3.0

    def test_category_enum_values(self):
        """All expected category values should exist."""
        expected = {"Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Drink"}
        actual = {c.value for c in Category}
        assert actual == expected


class TestIngredientModel:
    """Tests for the Ingredient model."""

    def test_ingredient_defaults(self, db):
        """Amount and unit should have sensible defaults."""
        r = Recipe(title="R", category=Category.DINNER)
        db.add(r)
        db.flush()
        ing = Ingredient(recipe_id=r.id, name="Salt")
        db.add(ing)
        db.commit()
        assert ing.amount == 0.0
        assert ing.unit == ""


class TestBookmarkModel:
    """Tests for the Bookmark model."""

    def test_unique_constraint(self, db):
        """A user cannot bookmark the same recipe twice."""
        import sqlalchemy
        user = User(username="bmu", email="bm@x.com",
                     password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.flush()
        r = Recipe(title="BmR", category=Category.DRINK, user_id=user.id)
        db.add(r)
        db.flush()
        db.add(Bookmark(user_id=user.id, recipe_id=r.id))
        db.commit()
        db.add(Bookmark(user_id=user.id, recipe_id=r.id))
        try:
            db.commit()
            assert False, "Expected IntegrityError"
        except sqlalchemy.exc.IntegrityError:
            db.rollback()
