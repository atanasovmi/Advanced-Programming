"""
app/views/home.py

The home page ("/") of the CookBook application.

Features:
  - Search bar to filter recipes by title / description
  - Category filter buttons
  - Responsive grid of recipe cards (title, category badge,
    average rating, prep/cook time)
  - Click on a card navigates to the recipe detail page
"""

from nicegui import ui

from app.models.database import SessionLocal
from app.models.recipe import Category
from app.services.recipe_service import RecipeService
from app.views.shared import page_layout, star_display, category_color


@ui.page("/")
def home_page() -> None:
    """Render the home page with recipe cards and filters."""

    # ------------------------------------------------------------------ #
    # State                                                                #
    # ------------------------------------------------------------------ #
    search_query: list[str] = [""]          # mutable wrapper for closure
    active_category: list[str] = ["all"]    # "all" or a Category value

    # ------------------------------------------------------------------ #
    # Helper: build / refresh the recipe grid                             #
    # ------------------------------------------------------------------ #
    def render_recipes(container: ui.column) -> None:
        """Clear *container* and re-render matching recipe cards."""
        container.clear()

        with SessionLocal() as db:
            # Apply search filter first, then category filter
            if search_query[0]:
                recipes = RecipeService.search(db, search_query[0])
            else:
                recipes = RecipeService.get_all(db)

            if active_category[0] != "all":
                cat = Category(active_category[0])
                recipes = [r for r in recipes if r.category == cat]

            if not recipes:
                with container:
                    ui.label("No recipes found 😕").classes(
                        "text-grey-5 text-xl text-center w-full mt-10"
                    )
                return

            # Snapshot data while session is open
            cards_data = [
                {
                    "id":          r.id,
                    "title":       r.title,
                    "description": r.description,
                    "category":    r.category,
                    "servings":    r.servings,
                    "total_time":  r.total_time,
                    "avg_rating":  round(r.average_rating, 1),
                    "num_ratings": len(r.ratings),
                }
                for r in recipes
            ]

        # Render outside the session to avoid DetachedInstanceError
        with container:
            with ui.grid(columns=3).classes("w-full gap-4"):
                for data in cards_data:
                    _recipe_card(data)

    def _recipe_card(data: dict) -> None:
        """Render a single clickable recipe card."""
        with ui.card().classes(
            "cursor-pointer hover:shadow-lg transition-shadow w-full"
        ).on("click", lambda d=data: ui.navigate.to(f"/recipe/{d['id']}")):

            # Category badge
            ui.badge(
                data["category"].value,
                color=category_color(data["category"])
            ).classes("text-xs")

            ui.label(data["title"]).classes("text-lg font-bold mt-1")
            ui.label(data["description"]).classes(
                "text-sm text-grey-6 line-clamp-2"
            )

            with ui.row().classes("items-center justify-between mt-2 w-full"):
                with ui.row().classes("items-center gap-1"):
                    star_display(data["avg_rating"])
                    ui.label(
                        f"({data['num_ratings']})"
                    ).classes("text-xs text-grey-5")

                with ui.row().classes("items-center gap-3 text-xs text-grey-6"):
                    ui.icon("schedule").classes("text-sm")
                    ui.label(f"{data['total_time']} min")
                    ui.icon("people").classes("text-sm")
                    ui.label(f"{data['servings']} servings")

    # ------------------------------------------------------------------ #
    # Page layout                                                         #
    # ------------------------------------------------------------------ #
    with page_layout("Home — CookBook"):

        # Page title
        ui.label("Discover Recipes").classes("text-3xl font-bold")

        # ---- Search bar ------------------------------------------------
        def on_search(e) -> None:
            search_query[0] = e.value.strip()
            render_recipes(recipe_grid)

        ui.input(
            placeholder="🔍  Search recipes by name or description …",
            on_change=on_search,
        ).classes("w-full").props("outlined clearable")

        # ---- Category filter chips ------------------------------------
        with ui.row().classes("gap-2 flex-wrap"):
            def make_filter(label: str, value: str) -> None:
                """Create a category filter chip."""
                def activate():
                    active_category[0] = value
                    render_recipes(recipe_grid)

                ui.chip(
                    label,
                    on_click=activate,
                ).props("outline clickable").classes("capitalize")

            make_filter("All", "all")
            for cat in Category:
                make_filter(cat.value, cat.value)

        # ---- Recipe grid (filled by render_recipes) -------------------
        recipe_grid = ui.column().classes("w-full")
        render_recipes(recipe_grid)
