"""User profile pages for public portfolios and private shortlist access."""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.user_service import UserService
from app.views.auth import get_current_user_id, get_current_username
from app.views.shared import page_layout, score_display, sector_color


@ui.page("/profile")
def own_profile_page() -> None:
    """Redirect the logged-in user to their public profile URL."""
    username = get_current_username()
    if not username:
        ui.navigate.to("/login")
        return
    ui.navigate.to(f"/profile/{username}")


@ui.page("/profile/{username}")
def profile_page(username: str) -> None:
    """Render the public profile page for a username."""
    current_user_id = get_current_user_id()

    with SessionLocal() as db:
        user = UserService.get_by_username(db, username)
        if user is None:
            with page_layout("Profile not found"):
                ui.label(f"No user named '{username}' found.").classes("text-2xl text-grey-5")
                ui.button("← Back to Explore", on_click=lambda: ui.navigate.to("/")).props("flat")
            return

        is_own_profile = current_user_id == user.id
        profile_data = {
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "created_at": user.created_at,
        }
        authored = [
            {
                "id": venture.id,
                "title": venture.title,
                "description": venture.description,
                "sector": venture.sector,
                "timeline_weeks": venture.timeline_weeks,
                "avg_score": round(venture.average_score, 1),
                "num_reviews": len(venture.reviews),
            }
            for venture in user.ventures
        ]
        shortlisted = []
        if is_own_profile:
            shortlisted = [
                {
                    "id": venture.id,
                    "title": venture.title,
                    "description": venture.description,
                    "sector": venture.sector,
                    "timeline_weeks": venture.timeline_weeks,
                    "avg_score": round(venture.average_score, 1),
                    "num_reviews": len(venture.reviews),
                    "author": venture.author.username if venture.author else None,
                }
                for venture in UserService.get_shortlisted_ventures(db, user.id)
            ]

    with page_layout(f"{profile_data['username']} — VentureCanvas"):
        with ui.card().classes("w-full"):
            with ui.row().classes("items-center justify-between w-full flex-wrap gap-4"):
                with ui.row().classes("items-center gap-4"):
                    initials = profile_data["username"][:2].upper()
                    ui.label(initials).classes(
                        "text-2xl font-bold text-white bg-slate-700 rounded-full w-14 h-14 flex items-center justify-center"
                    )
                    with ui.column().classes("gap-0"):
                        ui.label(profile_data["username"]).classes("text-2xl font-bold")
                        ui.label(
                            f"Member since {profile_data['created_at'].strftime('%B %Y')}"
                        ).classes("text-sm text-grey-5")
                with ui.row().classes("gap-4 text-center"):
                    with ui.column().classes("items-center gap-0"):
                        ui.label(str(len(authored))).classes("text-2xl font-bold text-slate-700")
                        ui.label("Ventures").classes("text-xs text-grey-5")
                    if is_own_profile:
                        with ui.column().classes("items-center gap-0"):
                            ui.label(str(len(shortlisted))).classes("text-2xl font-bold text-amber-600")
                            ui.label("Shortlisted").classes("text-xs text-grey-5")

            bio_label = ui.label(profile_data["bio"] if profile_data["bio"] else "No bio yet.").classes(
                "text-grey-7 mt-2" + (" italic" if not profile_data["bio"] else "")
            )

            if is_own_profile:
                with ui.expansion("✏️ Edit bio", icon="edit").classes("w-full mt-2"):
                    bio_edit = ui.textarea(
                        label="Your bio",
                        value=profile_data["bio"],
                        placeholder="Tell the community what kind of innovation work you enjoy.",
                    ).classes("w-full").props("outlined autogrow")

                    def save_bio() -> None:
                        with SessionLocal() as db:
                            UserService.update_bio(db, profile_data["id"], bio_edit.value or "")
                        bio_label.set_text(bio_edit.value or "No bio yet.")
                        ui.notify("Bio updated.", type="positive")

                    ui.button("Save", icon="save", on_click=save_bio).props("color=dark size=sm")

        ui.label(f"Venture briefs by {profile_data['username']} ({len(authored)})").classes("text-xl font-semibold mt-4")
        if authored:
            with ui.grid(columns=3).classes("w-full gap-4"):
                for data in authored:
                    _venture_card(data)
        else:
            ui.label("This user has not shared any venture briefs yet.").classes("text-grey-5 italic")

        if is_own_profile:
            ui.label(f"Your shortlist ({len(shortlisted)})").classes("text-xl font-semibold mt-4")
            if shortlisted:
                with ui.grid(columns=3).classes("w-full gap-4"):
                    for data in shortlisted:
                        _venture_card(data, show_author=True)
            else:
                ui.label(
                    "You have not shortlisted any ventures yet. Use the shortlist button on a venture detail page to save one here."
                ).classes("text-grey-5 italic")



def _venture_card(data: dict, show_author: bool = False) -> None:
    """Render a compact clickable venture card."""
    with ui.card().classes(
        "cursor-pointer hover:shadow-lg transition-shadow w-full"
    ).on("click", lambda d=data: ui.navigate.to(f"/venture/{d['id']}")):
        ui.badge(data["sector"].value, color=sector_color(data["sector"])).classes("text-xs")
        ui.label(data["title"]).classes("text-lg font-bold mt-1")
        ui.label(data["description"]).classes("text-sm text-grey-6 line-clamp-2")
        if show_author and data.get("author"):
            ui.label(f"by {data['author']}").classes("text-xs text-slate-600 italic")
        with ui.row().classes("items-center justify-between mt-2 w-full"):
            with ui.row().classes("items-center gap-1"):
                score_display(data["avg_score"])
                ui.label(f"({data['num_reviews']})").classes("text-xs text-grey-5")
            with ui.row().classes("items-center gap-1 text-xs text-grey-6"):
                ui.icon("schedule").classes("text-sm")
                ui.label(f"{data['timeline_weeks']} weeks")
