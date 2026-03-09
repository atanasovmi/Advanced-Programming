"""
main.py — CookBook Application Entry Point

Starts the NiceGUI / FastAPI server, initialises the database,
seeds it with sample data on the first run, and registers all
page routes.

Run with:
    python main.py

The application will be available at http://localhost:8080
"""

from nicegui import ui

# 1. Initialise the database schema (creates tables if they don't exist)
from app.models.database import init_db
init_db()

# 2. Seed the database with sample recipes on first run
from app.seed import seed_database
seed_database()

# 3. Register all page routes by importing the views package
import app.views  # noqa: F401, E402

# 4. Start the NiceGUI server
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="🍽️ CookBook",
        favicon="🍽️",
        port=8080,
        reload=False,
    )

