"""
app/models/database.py

Sets up the SQLAlchemy engine, session factory, and declarative base.
We use SQLite so no external database server is required.
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./venture_canvas.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""



def _migrate_schema() -> None:
    """Apply lightweight SQLite column-add migrations for existing tables."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue

        existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_cols:
                continue
            col_type = column.type.compile(dialect=engine.dialect)
            stmt = f"ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}"
            if column.default is not None and not callable(column.default.arg):
                stmt += f" DEFAULT {column.default.arg!r}"
            with engine.begin() as conn:
                conn.execute(text(stmt))



def init_db() -> None:
    """Create missing tables and apply lightweight schema migrations."""
    from app.models import milestone, resource_need, review, shortlist, user, venture  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_schema()
