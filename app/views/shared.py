"""Reusable layout and display helpers for VentureCanvas views."""

from contextlib import contextmanager

from nicegui import app as _app
from nicegui import ui

from app.models.venture import Sector

SECTOR_COLOR: dict[Sector, str] = {
    Sector.AI_DATA: "indigo",
    Sector.SUSTAINABILITY: "green",
    Sector.HEALTH: "red",
    Sector.EDUCATION: "orange",
    Sector.CULTURE: "purple",
    Sector.PRODUCTIVITY: "cyan",
}


def sector_color(sector: Sector) -> str:
    """Return the Quasar color used for the selected sector badge."""
    return SECTOR_COLOR.get(sector, "grey")


@contextmanager
def page_layout(title: str = "VentureCanvas"):
    """Wrap page content with a shared VentureCanvas header and footer."""
    current_username = _app.storage.user.get("username")

    with ui.header(elevated=True).classes("items-center justify-between bg-slate-800"):
        with ui.row().classes("items-center gap-3"):
            ui.label("🚀").classes("text-3xl")
            ui.label("VentureCanvas").classes(
                "text-2xl font-bold text-white cursor-pointer"
            ).on("click", lambda: ui.navigate.to("/"))

        with ui.row().classes("gap-2 items-center"):
            ui.button("Explore", icon="travel_explore", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
            ui.button("Submit Brief", icon="add_circle", on_click=lambda: ui.navigate.to("/submit")).props("flat color=white")
            ui.button("Resource Planner", icon="rule_folder", on_click=lambda: ui.navigate.to("/planner")).props("flat color=white")

            if current_username:
                ui.button(
                    current_username,
                    icon="account_circle",
                    on_click=lambda: ui.navigate.to(f"/profile/{current_username}"),
                ).props("flat color=white")
                ui.button("Logout", icon="logout", on_click=lambda: ui.navigate.to("/logout")).props("flat color=white")
            else:
                ui.button("Login", icon="login", on_click=lambda: ui.navigate.to("/login")).props("flat color=white")
                ui.button("Register", icon="person_add", on_click=lambda: ui.navigate.to("/register")).props("flat color=white")

    with ui.column().classes("w-full max-w-6xl mx-auto px-4 py-6 gap-6"):
        yield

    with ui.footer().classes("bg-grey-2 text-grey-7 text-center py-3"):
        ui.label("🚀 VentureCanvas — Innovation Portfolio Workspace · OOP Project 2026")



def score_display(score: float, max_stars: int = 5) -> None:
    """Render a row of filled, half, or empty stars for a review score."""
    with ui.row().classes("gap-0"):
        for i in range(1, max_stars + 1):
            if score >= i:
                ui.icon("star").classes("text-amber-500")
            elif score >= i - 0.5:
                ui.icon("star_half").classes("text-amber-500")
            else:
                ui.icon("star_border").classes("text-amber-500")
