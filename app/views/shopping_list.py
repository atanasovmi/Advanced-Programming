"""
app/views/shopping_list.py

The Shopping List page ("/shopping").

Allows the user to:
  1. Select one or more recipes using checkboxes.
  2. Click "Generate List" to aggregate all ingredients.
  3. View the consolidated list with combined amounts where
     the ingredient name AND unit are the same (e.g. two recipes
     both needing flour in grams will be merged into one entry).
"""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.recipe_service import RecipeService
from app.views.shared import page_layout


@ui.page("/shopping")
def shopping_list_page() -> None:
    """Render the shopping-list generator page."""

    # ------------------------------------------------------------------ #
    # Load all available recipes                                          #
    # ------------------------------------------------------------------ #
    with SessionLocal() as db:
        all_recipes = [
            {"id": r.id, "title": r.title}
            for r in RecipeService.get_all(db)
        ]

    # Track which recipe IDs the user has checked.
    selected_ids: set[int] = set()
    checkboxes: dict[int, ui.checkbox] = {}

    # ------------------------------------------------------------------ #
    # Generate the aggregated shopping list                               #
    # ------------------------------------------------------------------ #
    def generate(result_container: ui.column) -> None:
        """
        Read the checked recipes, aggregate their ingredients,
        and render the result inside *result_container*.
        """
        result_container.clear()

        if not selected_ids:
            with result_container:
                ui.label("Please select at least one recipe.").classes(
                    "text-warning"
                )
            return

        # Aggregate: key = (lower-cased name, lower-cased unit)
        aggregated: dict[tuple, dict] = {}

        with SessionLocal() as db:
            for recipe_id in selected_ids:
                recipe = RecipeService.get_by_id(db, recipe_id)
                if recipe is None:
                    continue
                for ing in recipe.ingredients:
                    key = (ing.name.lower(), ing.unit.lower())
                    if key in aggregated:
                        aggregated[key]["amount"] += ing.amount
                    else:
                        aggregated[key] = {
                            "name":   ing.name,
                            "amount": ing.amount,
                            "unit":   ing.unit,
                        }

        with result_container:
            if not aggregated:
                ui.label(
                    "The selected recipes have no ingredients listed."
                ).classes("text-grey-5 italic")
                return

            ui.label(
                f"Shopping List ({len(aggregated)} items)"
            ).classes("text-xl font-semibold")

            # Print button using browser print dialog
            ui.button(
                "🖨️  Print / Save as PDF",
                on_click=lambda: ui.run_javascript("window.print()"),
            ).props("outline color=grey-7 size=sm")

            with ui.list().props("dense separator").classes("w-full"):
                for item in sorted(aggregated.values(), key=lambda x: x["name"]):
                    amount_str = f"{item['amount']:g}" if item["amount"] else ""
                    unit_str   = item["unit"] if item["unit"] else ""
                    label_text = f"{item['name']} — {amount_str} {unit_str}".strip(" —")

                    with ui.item():
                        with ui.item_section().props("avatar"):
                            ui.icon("check_box_outline_blank").classes(
                                "text-orange-400"
                            )
                        with ui.item_section():
                            ui.item_label(label_text)

    # ------------------------------------------------------------------ #
    # Page layout                                                         #
    # ------------------------------------------------------------------ #
    with page_layout("Shopping List — CookBook"):
        ui.label("🛒 Shopping List Generator").classes("text-3xl font-bold")
        ui.label(
            "Select the recipes you want to cook and we'll combine "
            "all the ingredients into one handy list."
        ).classes("text-grey-6")

        # Create the result panel first so result_container is defined
        # before the Generate button's lambda captures it.
        with ui.row().classes("w-full gap-4 items-start flex-wrap"):

            # ---- Recipe selection panel ------------------------------
            with ui.card().classes("flex-1 min-w-64"):
                ui.label("Select Recipes").classes("text-lg font-semibold mb-2")

                if not all_recipes:
                    ui.label("No recipes in the database yet.").classes(
                        "text-grey-5 italic"
                    )
                else:
                    for recipe_data in all_recipes:
                        rid = recipe_data["id"]

                        def make_toggle(recipe_id: int) -> callable:
                            def toggle(e):
                                if e.value:
                                    selected_ids.add(recipe_id)
                                else:
                                    selected_ids.discard(recipe_id)
                            return toggle

                        cb = ui.checkbox(
                            recipe_data["title"],
                            on_change=make_toggle(rid),
                        )
                        checkboxes[rid] = cb

            # ---- Result panel ----------------------------------------
            # result_container is defined here and passed explicitly to
            # generate() so there is no ambiguity about which element
            # receives the aggregated list.
            with ui.card().classes("flex-2 min-w-72"):
                result_container = ui.column().classes("w-full gap-2")
                with result_container:
                    ui.label(
                        "Your shopping list will appear here."
                    ).classes("text-grey-5 italic")

        # The Generate button lives outside the two cards so it spans
        # the full width and its lambda has a clear reference to
        # result_container (defined in the result panel above).
        if all_recipes:
            ui.button(
                "Generate List",
                icon="shopping_cart",
                on_click=lambda: generate(result_container),
            ).props("color=orange")
