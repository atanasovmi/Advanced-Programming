"""
app/models/database.py

Sets up the SQLAlchemy engine, session factory, and declarative base.
We use SQLite so no external database server is required.
"""

from sqlalchemy import create_engine, inspect, text
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


def _migrate_schema() -> None:
    """
    Apply lightweight schema migrations for SQLite.

    ``Base.metadata.create_all()`` only creates *missing* tables; it does
    **not** add columns to tables that already exist.  This helper inspects
    every table that the ORM expects and adds any columns that are missing
    from the live database, preventing ``OperationalError: no such column``
    after a model is updated.

    Only new nullable / server-defaulted columns can be added this way.
    For complex migrations (renames, type changes) use Alembic.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue  # Will be created by create_all()

        existing_cols = {c["name"] for c in inspector.get_columns(table.name)}

        for column in table.columns:
            if column.name in existing_cols:
                continue

            # Build an ALTER TABLE statement for the missing column
            col_type = column.type.compile(dialect=engine.dialect)
            stmt = f"ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}"
            if column.default is not None and not callable(column.default.arg):
                stmt += f" DEFAULT {column.default.arg!r}"
            with engine.begin() as conn:
                conn.execute(text(stmt))


def init_db() -> None:
    """
    Create all database tables that do not yet exist and apply any
    pending lightweight schema migrations.

    This function is called once at application startup.
    It is safe to call multiple times – SQLAlchemy only creates
    tables that are missing, leaving existing data untouched.
    """
    # Import all models here so SQLAlchemy knows about them before
    # it tries to create the schema.
    from app.models import recipe, ingredient, step, rating, user, bookmark  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_schema()
