"""
app/views/add_recipe.py

The "Add New Recipe" page ("/add").

Provides a multi-section form where the user can enter:
  - Basic info (title, description, category, servings, times)
  - A dynamic list of ingredients (add / remove rows)
  - A dynamic list of instruction steps (add / remove rows)

If the user is logged in the new recipe is attributed to their account.
On successful submission the user is redirected to the new recipe's
detail page.
"""

from nicegui import ui

from app.models.database import SessionLocal
from app.models.recipe import Category
from app.services.recipe_service import RecipeService
from app.views.shared import page_layout
from app.views.auth import get_current_user_id, get_current_username


@ui.page("/add")
def add_recipe_page() -> None:
    """Render the add-recipe form."""

    current_user_id = get_current_user_id()
    current_username = get_current_username()

    # ------------------------------------------------------------------ #
    # State: dynamic ingredient & step rows                               #
    # ------------------------------------------------------------------ #
    ingredient_rows: list[dict] = []
    step_rows: list[ui.textarea] = []

    ingredient_container: ui.column
    step_container: ui.column

    # ------------------------------------------------------------------ #
    # Helpers: add / remove dynamic rows                                  #
    # ------------------------------------------------------------------ #
    def add_ingredient_row() -> None:
        """Append a new ingredient input row to the form."""
        with ingredient_container:
            row_ref: dict = {}
            with ui.row().classes("w-full gap-2 items-center") as row_el:
                row_ref["name"] = ui.input(
                    placeholder="e.g. Flour"
                ).classes("flex-2").props("outlined dense")
                row_ref["amount"] = ui.number(
                    placeholder="250", min=0
                ).classes("w-24").props("outlined dense")
                row_ref["unit"] = ui.input(
                    placeholder="g"
                ).classes("w-20").props("outlined dense")

                def make_remover(row_dict: dict, element) -> callable:
                    def remove():
                        if row_dict in ingredient_rows:
                            ingredient_rows.remove(row_dict)
                        element.delete()
                    return remove

                ui.button(
                    icon="remove_circle_outline",
                    on_click=make_remover(row_ref, row_el),
                ).props("flat round color=red-4 dense")
            ingredient_rows.append(row_ref)

    def add_step_row() -> None:
        """Append a new instruction step textarea to the form."""
        step_num = len(step_rows) + 1
        with step_container:
            with ui.row().classes("w-full gap-2 items-start") as row_el:
                ui.badge(str(step_num), color="teal").classes(
                    "mt-2 min-w-6 h-6 flex items-center justify-center"
                )
                step_input = ui.textarea(
                    placeholder=f"Step {step_num}: describe what to do …",
                ).classes("flex-1").props("outlined dense autogrow")

                def make_step_remover(inp: ui.textarea, element) -> callable:
                    def remove():
                        if inp in step_rows:
                            step_rows.remove(inp)
                        element.delete()
                    return remove

                ui.button(
                    icon="remove_circle_outline",
                    on_click=make_step_remover(step_input, row_el),
                ).props("flat round color=red-4 dense")
            step_rows.append(step_input)

    # ------------------------------------------------------------------ #
    # Submit handler                                                       #
    # ------------------------------------------------------------------ #
    def submit_form(
        title_input: ui.input,
        desc_input: ui.textarea,
        category_select,
        servings_input: ui.number,
        prep_input: ui.number,
        cook_input: ui.number,
    ) -> None:
        """Collect form values, validate, and persist the new recipe."""

        ingredients = []
        for row in ingredient_rows:
            name = (row["name"].value or "").strip()
            if not name:
                continue
            ingredients.append({
                "name":   name,
                "amount": row["amount"].value or 0,
                "unit":   (row["unit"].value or "").strip(),
            })

        steps = [
            (s.value or "").strip()
            for s in step_rows
            if (s.value or "").strip()
        ]

        try:
            with SessionLocal() as db:
                recipe = RecipeService.create(
                    db=db,
                    title=title_input.value or "",
                    description=desc_input.value or "",
                    category=Category(category_select.value),
                    servings=int(servings_input.value or 2),
                    prep_time=int(prep_input.value or 0),
                    cook_time=int(cook_input.value or 0),
                    ingredients=ingredients,
                    steps=steps,
                    user_id=current_user_id,  # attribute to logged-in user
                )
            ui.notify(
                f"'{recipe.title}' saved successfully! 🎉",
                type="positive"
            )
            ui.navigate.to(f"/recipe/{recipe.id}")
        except ValueError as err:
            ui.notify(str(err), type="negative")

    # ------------------------------------------------------------------ #
    # Page layout                                                         #
    # ------------------------------------------------------------------ #
    with page_layout("Add Recipe — RecipeVault"):
        ui.label("Add a New Recipe").classes("text-3xl font-bold")

        # Show which user is adding this recipe
        if current_username:
            with ui.row().classes("items-center gap-1 text-sm text-teal-700"):
                ui.icon("account_circle").classes("text-sm")
                ui.label(f"This recipe will be attributed to your account: ")
                ui.label(current_username).classes("font-semibold")
        else:
            with ui.row().classes(
                "items-center gap-2 bg-amber-50 border border-amber-300 "
                "rounded p-3 text-sm text-amber-800"
            ):
                ui.icon("info").classes("text-amber-600")
                ui.label(
                    "You are adding this recipe as a guest. "
                    "Log in to have recipes attributed to your profile."
                )
                ui.button(
                    "Login", icon="login",
                    on_click=lambda: ui.navigate.to("/login"),
                ).props("flat color=amber-8 dense size=sm")

        ui.button(
            "← Back to Home",
            on_click=lambda: ui.navigate.to("/")
        ).props("flat size=sm")

        # ---- Basic info card -----------------------------------------
        with ui.card().classes("w-full"):
            ui.label("Basic Information").classes("text-lg font-semibold mb-2")
            with ui.column().classes("w-full gap-3"):
                title_input = ui.input(
                    label="Recipe Title *",
                    placeholder="e.g. Classic Spaghetti Carbonara",
                ).classes("w-full").props("outlined")

                desc_input = ui.textarea(
                    label="Short Description",
                    placeholder="A brief description that will appear on the recipe card …",
                ).classes("w-full").props("outlined autogrow")

                with ui.row().classes("w-full gap-3 flex-wrap"):
                    category_select = ui.select(
                        label="Category *",
                        options={c.value: c.value for c in Category},
                        value=Category.DINNER.value,
                    ).classes("flex-1 min-w-40").props("outlined")

                    servings_input = ui.number(
                        label="Servings", value=2, min=1
                    ).classes("w-28").props("outlined")

                    prep_input = ui.number(
                        label="Prep Time (min)", value=0, min=0
                    ).classes("w-36").props("outlined")

                    cook_input = ui.number(
                        label="Cook Time (min)", value=0, min=0
                    ).classes("w-36").props("outlined")

        # ---- Ingredients card ----------------------------------------
        with ui.card().classes("w-full"):
            ui.label("Ingredients").classes("text-lg font-semibold")
            ui.label(
                "Name · Amount · Unit (e.g. Flour · 250 · g)"
            ).classes("text-xs text-grey-5 mb-2")

            ingredient_container = ui.column().classes("w-full gap-2")

            add_ingredient_row()
            add_ingredient_row()
            add_ingredient_row()

            ui.button(
                "Add Ingredient", icon="add",
                on_click=add_ingredient_row,
            ).props("outline color=teal size=sm")

        # ---- Steps card ----------------------------------------------
        with ui.card().classes("w-full"):
            ui.label("Instructions").classes("text-lg font-semibold mb-2")

            step_container = ui.column().classes("w-full gap-2")

            add_step_row()
            add_step_row()

            ui.button(
                "Add Step", icon="add",
                on_click=add_step_row,
            ).props("outline color=teal size=sm")

        # ---- Submit -------------------------------------------------
        ui.button(
            "💾  Save Recipe",
            on_click=lambda: submit_form(
                title_input, desc_input,
                category_select,
                servings_input, prep_input, cook_input,
            ),
        ).props("color=teal size=lg").classes("self-end")
