"""Registers all NiceGUI page routes for VentureCanvas."""

from app.views import add_venture, auth, home, profile, resource_planner, venture_detail  # noqa: F401

__all__ = [
    "home",
    "venture_detail",
    "add_venture",
    "resource_planner",
    "auth",
    "profile",
]
