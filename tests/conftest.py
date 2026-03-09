"""
Shared pytest fixtures for RecipeVault tests.

Every test gets its own in-memory SQLite database so tests are
completely isolated and do not affect the production ``cookbook.db``.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base

# Import all models so Base.metadata knows about them
from app.models.user import User  # noqa: F401
from app.models.recipe import Recipe  # noqa: F401
from app.models.ingredient import Ingredient  # noqa: F401
from app.models.step import Step  # noqa: F401
from app.models.rating import Rating  # noqa: F401
from app.models.bookmark import Bookmark  # noqa: F401


@pytest.fixture()
def db():
    """
    Yield a SQLAlchemy Session backed by an in-memory SQLite database.

    Tables are created fresh for every test and torn down afterwards.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
