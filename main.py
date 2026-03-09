"""
main.py -- VentureCanvas application entry point.

Starts the NiceGUI / FastAPI server, initialises the database,
seeds it with demo users and sample venture briefs on the first run,
and registers all page routes.

Run with:
    python main.py

The application will be available at http://localhost:8080

Demo accounts (created on first run):
    username: alice   password: alice123
    username: bob     password: bob12345
"""

from nicegui import ui

from app.models.database import init_db

init_db()

from app.seed import seed_database
seed_database()

import app.views  # noqa: F401, E402

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="VentureCanvas",
        favicon="🚀",
        port=8080,
        reload=False,
        storage_secret="venturecanvas-oop-project-2026-secret",
    )
