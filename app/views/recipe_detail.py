"""
app/views/recipe_detail.py

The recipe detail page ("/recipe/{id}").

Shows:
  - Recipe title, author, category, servings, time info
  - Ingredients list
  - Numbered step-by-step instructions
  - Average star rating and all user reviews
  - Form to submit a new rating
  - Bookmark button (logged-in users)
  - Delete button to remove the recipe
"""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.recipe_service import RecipeService
from app.services.rating_service import RatingService
from app.services.user_service import UserService
from app.views.shared import page_layout, star_display, category_color
from app.views.auth import get_current_user_id


@ui.page("/recipe/{recipe_id}")
def recipe_detail_page(recipe_id: int) -> None:
    """Render the detail view for a single recipe."""

    current_user_id = get_current_user_id()

    # ------------------------------------------------------------------ #
    # Load data                                                           #
    # ------------------------------------------------------------------ #
    with SessionLocal() as db:
        recipe = RecipeService.get_by_id(db, recipe_id)
        if recipe is None:
            with page_layout("Not Found"):
                ui.label("Recipe not found 😕").classes("text-2xl text-grey-5")
                ui.button(
                    "← Back to Home",
                    on_click=lambda: ui.navigate.to("/")
                ).props("flat")
            return

        # Snapshot all data while the session is open
        data = {
            "id":          recipe.id,
            "title":       recipe.title,
            "description": recipe.description,
            "category":    recipe.category,
            "servings":    recipe.servings,
            "prep_time":   recipe.prep_time,
            "cook_time":   recipe.cook_time,
            "total_time":  recipe.total_time,
            "avg_rating":  round(recipe.average_rating, 1),
            "author_id":   recipe.user_id,
            "author":      recipe.author.username if recipe.author else None,
            "ingredients": [
                {"name": i.name, "amount": i.amount, "unit": i.unit}
                for i in recipe.ingredients
            ],
            "steps": [s.description for s in recipe.steps],
            "ratings": [
                {"score": r.score, "comment": r.comment, "date": r.created_at}
                for r in recipe.ratings
            ],
        }

        # Check bookmark status for logged-in user
        is_bookmarked = (
            UserService.is_bookmarked(db, current_user_id, recipe_id)
            if current_user_id else False
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #
    def refresh_ratings(container: ui.column) -> None:
        """Reload and re-render the ratings section."""
        container.clear()
        with SessionLocal() as db:
            ratings = RatingService.get_for_recipe(db, recipe_id)
            snapshot = [
                {"score": r.score, "comment": r.comment, "date": r.created_at}
                for r in ratings
            ]
        with container:
            _render_ratings(snapshot)

    def _render_ratings(ratings: list[dict]) -> None:
        """Render the list of rating cards."""
        if not ratings:
            ui.label("No ratings yet — be the first!").classes("text-grey-5 italic")
            return
        for r in ratings:
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center gap-2"):
                    star_display(r["score"])
                    ui.label(
                        r["date"].strftime("%d %b %Y")
                    ).classes("text-xs text-grey-5 ml-auto")
                if r["comment"]:
                    ui.label(r["comment"]).classes("text-sm text-grey-7 mt-1")

    def submit_rating(score_ref: list, comment_input: ui.input,
                      rating_container: ui.column) -> None:
        """Validate and persist the submitted rating."""
        score = score_ref[0]
        if score == 0:
            ui.notify("Please select a star rating.", type="warning")
            return
        comment = comment_input.value or ""
        try:
            with SessionLocal() as db:
                RatingService.submit(db, recipe_id, score, comment)
            ui.notify("Rating submitted — thank you! ⭐", type="positive")
            comment_input.set_value("")
            score_ref[0] = 0
            refresh_ratings(rating_container)
        except ValueError as err:
            ui.notify(str(err), type="negative")

    def delete_recipe() -> None:
        """Delete this recipe and navigate back home."""
        with SessionLocal() as db:
            RecipeService.delete(db, recipe_id)
        ui.notify("Recipe deleted.", type="info")
        ui.navigate.to("/")

    # ------------------------------------------------------------------ #
    # Page layout                                                         #
    # ------------------------------------------------------------------ #
    with page_layout(data["title"]):

        # ---- Breadcrumb / back button --------------------------------
        ui.button(
            "← Back to Home",
            on_click=lambda: ui.navigate.to("/")
        ).props("flat size=sm")

        # ---- Header card ---------------------------------------------
        with ui.card().classes("w-full"):
            with ui.row().classes("items-start justify-between w-full flex-wrap gap-4"):
                with ui.column().classes("gap-1"):
                    ui.badge(
                        data["category"].value,
                        color=category_color(data["category"])
                    )
                    ui.label(data["title"]).classes("text-3xl font-bold")
                    ui.label(data["description"]).classes("text-grey-7")

                    # Author attribution
                    if data["author"]:
                        with ui.row().classes("items-center gap-1 mt-1"):
                            ui.icon("person").classes("text-sm text-teal-600")
                            ui.link(
                                f"by {data['author']}",
                                f"/profile/{data['author']}"
                            ).classes("text-sm text-teal-600 italic")

                    with ui.row().classes("gap-6 mt-2 text-sm text-grey-6"):
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("schedule")
                            ui.label(f"Prep: {data['prep_time']} min")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("local_fire_department")
                            ui.label(f"Cook: {data['cook_time']} min")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("timer")
                            ui.label(f"Total: {data['total_time']} min")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("people")
                            ui.label(f"{data['servings']} servings")

                # Top-right: average rating + bookmark button
                with ui.column().classes("items-center gap-2"):
                    star_display(data["avg_rating"])
                    ui.label(
                        f"{data['avg_rating']} / 5.0  ({len(data['ratings'])} ratings)"
                    ).classes("text-sm text-grey-6")

                    # Bookmark button for logged-in users
                    if current_user_id:
                        bookmarked_state: list[bool] = [is_bookmarked]

                        # Props constants to avoid duplication
                        _BM_ACTIVE   = ("Bookmarked", "bookmark",        "color=teal outline")
                        _BM_INACTIVE = ("Bookmark",   "bookmark_border", "color=grey-6 outline")

                        _lbl, _ico, _props = _BM_ACTIVE if is_bookmarked else _BM_INACTIVE
                        bookmark_btn = ui.button(_lbl, icon=_ico).props(_props)

                        def toggle_bookmark() -> None:
                            with SessionLocal() as db:
                                if bookmarked_state[0]:
                                    UserService.remove_bookmark(
                                        db, current_user_id, recipe_id
                                    )
                                    bookmarked_state[0] = False
                                    lbl, ico, props = _BM_INACTIVE
                                    ui.notify("Bookmark removed.", type="info")
                                else:
                                    UserService.add_bookmark(
                                        db, current_user_id, recipe_id
                                    )
                                    bookmarked_state[0] = True
                                    lbl, ico, props = _BM_ACTIVE
                                    ui.notify("Recipe bookmarked! 🔖", type="positive")
                            bookmark_btn.set_text(lbl)
                            bookmark_btn.props(f"icon={ico} {props}")

                        bookmark_btn.on("click", toggle_bookmark)
                    else:
                        ui.button(
                            "Login to bookmark",
                            icon="bookmark_border",
                            on_click=lambda: ui.navigate.to("/login"),
                        ).props("flat color=grey-5 size=sm")

        # ---- Two-column layout: Ingredients | Steps ------------------
        with ui.row().classes("w-full gap-4 items-start flex-wrap"):

            # Ingredients
            with ui.card().classes("flex-1 min-w-64"):
                ui.label("Ingredients").classes("text-xl font-semibold mb-2")
                if data["ingredients"]:
                    with ui.list().props("dense separator"):
                        for ing in data["ingredients"]:
                            amount_str = (
                                f"{ing['amount']:g}" if ing["amount"] else ""
                            )
                            unit_str = ing["unit"] if ing["unit"] else ""
                            label = f"{amount_str} {unit_str} {ing['name']}".strip()
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.icon("fiber_manual_record").classes(
                                        "text-xs text-teal-400"
                                    )
                                with ui.item_section():
                                    ui.item_label(label)
                else:
                    ui.label("No ingredients listed.").classes("text-grey-5 italic")

            # Steps
            with ui.card().classes("flex-2 min-w-64"):
                ui.label("Instructions").classes("text-xl font-semibold mb-2")
                if data["steps"]:
                    for idx, step_text in enumerate(data["steps"], start=1):
                        with ui.row().classes("items-start gap-3 mb-3"):
                            ui.badge(
                                str(idx), color="teal"
                            ).classes("mt-1 min-w-6 h-6 flex items-center justify-center")
                            ui.label(step_text).classes("text-sm flex-1")
                else:
                    ui.label("No instructions listed.").classes("text-grey-5 italic")

        # ---- Ratings section ----------------------------------------
        with ui.card().classes("w-full"):
            ui.label("Reviews").classes("text-xl font-semibold mb-2")

            rating_container = ui.column().classes("w-full gap-2")
            _render_ratings(data["ratings"])

            ui.separator()
            ui.label("Leave a review").classes("text-lg font-medium mt-2")

            # Star picker -----------------------------------------------
            selected_score: list[int] = [0]   # mutable single-item list

            with ui.row().classes("gap-1 cursor-pointer"):
                star_icons: list[ui.icon] = []

                def make_star_click(i: int) -> callable:
                    """Return a click handler that sets the score to *i*."""
                    def on_star_click():
                        selected_score[0] = i
                        for j, icon in enumerate(star_icons, start=1):
                            icon.props(
                                "color=yellow-8" if j <= i else "color=grey-4"
                            )
                    return on_star_click

                for star_i in range(1, 6):
                    icon = ui.icon("star").classes("text-3xl text-grey-4")
                    icon.on("click", make_star_click(star_i))
                    star_icons.append(icon)

            comment_input = ui.input(
                label="Comment (optional)",
                placeholder="Share your thoughts about this recipe …",
            ).classes("w-full").props("outlined")

            ui.button(
                "Submit Rating",
                icon="send",
                on_click=lambda: submit_rating(
                    selected_score, comment_input, rating_container
                ),
            ).props("color=teal")

        # ---- Danger zone: delete ------------------------------------
        with ui.expansion("⚠️ Danger Zone", icon="warning").classes(
            "w-full text-red-600"
        ):
            ui.label(
                "Deleting a recipe is permanent and cannot be undone."
            ).classes("text-sm text-grey-6 mb-2")
            ui.button(
                "Delete this recipe",
                icon="delete",
                on_click=delete_recipe,
            ).props("color=negative outline")
