"""
app/views/profile.py

User profile pages:
  /profile          — the currently logged-in user's own profile
  /profile/{username} — any user's public profile

Shows:
  - Display name, bio, member since
  - Recipes authored by the user
  - Bookmarked recipes (own profile only)
  - Edit-bio form (own profile only)
"""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.user_service import UserService
from app.services.recipe_service import RecipeService
from app.views.shared import page_layout, star_display, category_color
from app.views.auth import get_current_user_id, get_current_username


# ---------------------------------------------------------------------------
# /profile  →  redirect to /profile/<own username>
# ---------------------------------------------------------------------------

@ui.page("/profile")
def own_profile_page() -> None:
    """Redirect the logged-in user to their public profile URL."""
    username = get_current_username()
    if not username:
        ui.navigate.to("/login")
        return
    ui.navigate.to(f"/profile/{username}")


# ---------------------------------------------------------------------------
# /profile/{username}
# ---------------------------------------------------------------------------

@ui.page("/profile/{username}")
def profile_page(username: str) -> None:
    """Render the public profile for *username*."""

    current_user_id = get_current_user_id()

    # ------------------------------------------------------------------ #
    # Load profile data                                                    #
    # ------------------------------------------------------------------ #
    with SessionLocal() as db:
        user = UserService.get_by_username(db, username)

        if user is None:
            with page_layout("Profile not found — RecipeVault"):
                ui.label(f"No user named '{username}' found. 😕").classes(
                    "text-2xl text-grey-5"
                )
                ui.button(
                    "← Back to Home", on_click=lambda: ui.navigate.to("/")
                ).props("flat")
            return

        is_own_profile = current_user_id == user.id

        profile_data = {
            "id":         user.id,
            "username":   user.username,
            "bio":        user.bio,
            "created_at": user.created_at,
        }

        # Authored recipes
        authored = [
            {
                "id":          r.id,
                "title":       r.title,
                "description": r.description,
                "category":    r.category,
                "total_time":  r.total_time,
                "avg_rating":  round(r.average_rating, 1),
                "num_ratings": len(r.ratings),
            }
            for r in user.recipes
        ]

        # Bookmarked recipes (own profile only)
        bookmarked = []
        if is_own_profile:
            for r in UserService.get_bookmarked_recipes(db, user.id):
                bookmarked.append(
                    {
                        "id":          r.id,
                        "title":       r.title,
                        "description": r.description,
                        "category":    r.category,
                        "total_time":  r.total_time,
                        "avg_rating":  round(r.average_rating, 1),
                        "num_ratings": len(r.ratings),
                        "author":      r.author.username if r.author else None,
                    }
                )

    # ------------------------------------------------------------------ #
    # Page layout                                                          #
    # ------------------------------------------------------------------ #
    with page_layout(f"{profile_data['username']} — RecipeVault"):

        # ---- Profile header card ------------------------------------
        with ui.card().classes("w-full"):
            with ui.row().classes(
                "items-center justify-between w-full flex-wrap gap-4"
            ):
                with ui.row().classes("items-center gap-4"):
                    # Avatar: initials in a coloured circle
                    initials = profile_data["username"][:2].upper()
                    ui.label(initials).classes(
                        "text-2xl font-bold text-white bg-teal-500 "
                        "rounded-full w-14 h-14 flex items-center justify-center"
                    )
                    with ui.column().classes("gap-0"):
                        ui.label(profile_data["username"]).classes(
                            "text-2xl font-bold"
                        )
                        ui.label(
                            f"Member since "
                            f"{profile_data['created_at'].strftime('%B %Y')}"
                        ).classes("text-sm text-grey-5")

                with ui.row().classes("gap-4 text-center"):
                    with ui.column().classes("items-center gap-0"):
                        ui.label(str(len(authored))).classes(
                            "text-2xl font-bold text-teal-600"
                        )
                        ui.label("Recipes").classes("text-xs text-grey-5")
                    if is_own_profile:
                        with ui.column().classes("items-center gap-0"):
                            ui.label(str(len(bookmarked))).classes(
                                "text-2xl font-bold text-orange-500"
                            )
                            ui.label("Bookmarks").classes("text-xs text-grey-5")

            # Bio section
            bio_label = ui.label(
                profile_data["bio"] if profile_data["bio"] else "No bio yet."
            ).classes(
                "text-grey-7 mt-2"
                + (" italic" if not profile_data["bio"] else "")
            )

            # Edit-bio form (own profile only)
            if is_own_profile:
                with ui.expansion("✏️  Edit bio", icon="edit").classes(
                    "w-full mt-2"
                ):
                    bio_edit = ui.textarea(
                        label="Your bio",
                        value=profile_data["bio"],
                        placeholder="Tell the community about yourself …",
                    ).classes("w-full").props("outlined autogrow")

                    def save_bio() -> None:
                        with SessionLocal() as db:
                            UserService.update_bio(
                                db, profile_data["id"], bio_edit.value or ""
                            )
                        bio_label.set_text(bio_edit.value or "No bio yet.")
                        ui.notify("Bio updated! ✅", type="positive")

                    ui.button(
                        "Save", icon="save", on_click=save_bio
                    ).props("color=teal size=sm")

        # ---- Authored recipes ----------------------------------------
        ui.label(
            f"Recipes by {profile_data['username']} ({len(authored)})"
        ).classes("text-xl font-semibold mt-4")

        if authored:
            with ui.grid(columns=3).classes("w-full gap-4"):
                for data in authored:
                    _recipe_card(data)
        else:
            ui.label(
                "This user hasn't shared any recipes yet."
            ).classes("text-grey-5 italic")

        # ---- Bookmarked recipes (own profile) -----------------------
        if is_own_profile:
            ui.label(
                f"Your Bookmarks ({len(bookmarked)})"
            ).classes("text-xl font-semibold mt-4")

            if bookmarked:
                with ui.grid(columns=3).classes("w-full gap-4"):
                    for data in bookmarked:
                        _recipe_card(data, show_author=True)
            else:
                ui.label(
                    "You haven't bookmarked any recipes yet. "
                    "Tap the 🔖 icon on a recipe to save it here."
                ).classes("text-grey-5 italic")


# ---------------------------------------------------------------------------
# Shared card helper
# ---------------------------------------------------------------------------

def _recipe_card(data: dict, show_author: bool = False) -> None:
    """Render a compact clickable recipe card."""
    with ui.card().classes(
        "cursor-pointer hover:shadow-lg transition-shadow w-full"
    ).on("click", lambda d=data: ui.navigate.to(f"/recipe/{d['id']}")):

        ui.badge(
            data["category"].value,
            color=category_color(data["category"])
        ).classes("text-xs")

        ui.label(data["title"]).classes("text-lg font-bold mt-1")
        ui.label(data["description"]).classes(
            "text-sm text-grey-6 line-clamp-2"
        )

        if show_author and data.get("author"):
            ui.label(f"by {data['author']}").classes(
                "text-xs text-teal-600 italic"
            )

        with ui.row().classes("items-center justify-between mt-2 w-full"):
            with ui.row().classes("items-center gap-1"):
                star_display(data["avg_rating"])
                ui.label(f"({data['num_ratings']})").classes(
                    "text-xs text-grey-5"
                )
            with ui.row().classes("items-center gap-1 text-xs text-grey-6"):
                ui.icon("schedule").classes("text-sm")
                ui.label(f"{data['total_time']} min")
