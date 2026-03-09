"""Shared pytest fixtures for VentureCanvas tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base

from app.models.milestone import Milestone  # noqa: F401
from app.models.resource_need import ResourceNeed  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.shortlist import Shortlist  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.venture import Venture  # noqa: F401


@pytest.fixture()
def db():
    """Yield an isolated in-memory SQLite database session for each test."""
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
