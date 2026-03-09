"""
app/views/shared.py

Reusable helper components used across multiple views:
  - page_layout: header + footer wrapper
  - star_display: render filled/empty star icons for a rating
  - category_color: map Category → Quasar colour name
"""

from contextlib import contextmanager
from nicegui import ui
from app.models.recipe import Category


# Map each category to a Quasar/Tailwind colour used for badges.
CATEGORY_COLOR: dict[Category, str] = {
    Category.BREAKFAST: "orange",
    Category.LUNCH:     "green",
    Category.DINNER:    "blue",
    Category.DESSERT:   "pink",
    Category.SNACK:     "purple",
    Category.DRINK:     "cyan",
}


def category_color(category: Category) -> str:
    """Return the Quasar colour name for the given category."""
    return CATEGORY_COLOR.get(category, "grey")


@contextmanager
def page_layout(title: str = "🍽️ CookBook"):
    """
    Context manager that wraps page content with a consistent
    header navigation bar and a footer.

    Usage::

        with page_layout("My Page"):
            ui.label("Hello!")
    """
    # ---- Header --------------------------------------------------------
    with ui.header(elevated=True).classes("items-center justify-between bg-orange-600"):
        with ui.row().classes("items-center gap-4"):
            ui.label("🍽️").classes("text-3xl")
            ui.label("CookBook").classes("text-2xl font-bold text-white")

        with ui.row().classes("gap-2"):
            ui.button(
                "Home", icon="home",
                on_click=lambda: ui.navigate.to("/")
            ).props("flat color=white")
            ui.button(
                "Add Recipe", icon="add",
                on_click=lambda: ui.navigate.to("/add")
            ).props("flat color=white")
            ui.button(
                "Shopping List", icon="shopping_cart",
                on_click=lambda: ui.navigate.to("/shopping")
            ).props("flat color=white")

    # ---- Page body (caller fills this) ---------------------------------
    with ui.column().classes("w-full max-w-6xl mx-auto px-4 py-6 gap-6"):
        yield

    # ---- Footer --------------------------------------------------------
    with ui.footer().classes("bg-grey-2 text-grey-7 text-center py-3"):
        ui.label("🍽️ CookBook — OOP Project 2026")


def star_display(score: float, max_stars: int = 5) -> None:
    """
    Render a row of filled, half, or empty star icons.

    Args:
        score:     Average rating value (e.g. 3.7).
        max_stars: Total number of stars to render (default 5).
    """
    with ui.row().classes("gap-0"):
        for i in range(1, max_stars + 1):
            if score >= i:
                ui.icon("star").classes("text-yellow-500")
            elif score >= i - 0.5:
                ui.icon("star_half").classes("text-yellow-500")
            else:
                ui.icon("star_border").classes("text-yellow-500")
