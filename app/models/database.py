"""
app/models/database.py

Sets up the SQLAlchemy engine, session factory, and declarative base.
We use SQLite so no external database server is required.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# The database file will be created in the project root directory.
DATABASE_URL = "sqlite:///./cookbook.db"

# create_engine() creates the connection pool. check_same_thread=False
# is required for SQLite when used with a web server that may access
# the database from multiple threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True to see SQL statements in the console
)

# SessionLocal is a factory that produces individual database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def init_db() -> None:
    """
    Create all database tables that do not yet exist.

    This function is called once at application startup.
    It is safe to call multiple times – SQLAlchemy only creates
    tables that are missing, leaving existing data untouched.
    """
    # Import all models here so SQLAlchemy knows about them before
    # it tries to create the schema.
    from app.models import recipe, ingredient, step, rating  # noqa: F401
    Base.metadata.create_all(bind=engine)
