"""
main.py -- RecipeVault Application Entry Point

Starts the NiceGUI / FastAPI server, initialises the database,
seeds it with demo users and sample recipes on the first run,
and registers all page routes.

Run with:
    python main.py

The application will be available at http://localhost:8080

Demo accounts (created on first run):
    username: alice   password: alice123
    username: bob     password: bob12345
"""

from nicegui import ui

# 1. Initialise the database schema (creates tables if they don't exist)
from app.models.database import init_db
init_db()

# 2. Seed the database with demo users and sample recipes on first run
from app.seed import seed_database
seed_database()

# 3. Register all page routes by importing the views package
import app.views  # noqa: F401, E402

# 4. Start the NiceGUI server
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="RecipeVault",
        favicon="🍳",
        port=8080,
        reload=False,
        # storage_secret is required for app.storage.user (session cookies).
        # Change this to a long random string in production.
        storage_secret="recipevault-oop-project-2026-secret",
    )
