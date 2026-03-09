"""Detail page for a single venture brief with reviews and shortlist actions."""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.review_service import ReviewService
from app.services.user_service import UserService
from app.services.venture_service import VentureService
from app.views.auth import get_current_user_id
from app.views.shared import page_layout, score_display, sector_color


@ui.page("/venture/{venture_id}")
def venture_detail_page(venture_id: int) -> None:
    """Render the detail view for a single venture brief."""
    current_user_id = get_current_user_id()

    with SessionLocal() as db:
        venture = VentureService.get_by_id(db, venture_id)
        if venture is None:
            with page_layout("Not Found"):
                ui.label("Venture brief not found.").classes("text-2xl text-grey-5")
                ui.button("← Back to Explore", on_click=lambda: ui.navigate.to("/")).props("flat")
            return

        data = {
            "id": venture.id,
            "title": venture.title,
            "description": venture.description,
            "sector": venture.sector,
            "team_size": venture.team_size,
            "discovery_weeks": venture.discovery_weeks,
            "build_weeks": venture.build_weeks,
            "timeline_weeks": venture.timeline_weeks,
            "avg_score": round(venture.average_score, 1),
            "author": venture.author.username if venture.author else None,
            "resource_needs": [
                {"name": item.name, "effort": item.effort, "unit": item.unit}
                for item in venture.resource_needs
            ],
            "milestones": [milestone.description for milestone in venture.milestones],
            "reviews": [
                {"score": review.score, "comment": review.comment, "date": review.created_at}
                for review in venture.reviews
            ],
        }
        is_shortlisted = (
            UserService.is_shortlisted(db, current_user_id, venture_id)
            if current_user_id
            else False
        )

    def refresh_reviews(container: ui.column) -> None:
        container.clear()
        with SessionLocal() as db:
            reviews = ReviewService.get_for_venture(db, venture_id)
            snapshot = [
                {"score": review.score, "comment": review.comment, "date": review.created_at}
                for review in reviews
            ]
        with container:
            render_reviews(snapshot)

    def render_reviews(reviews: list[dict]) -> None:
        if not reviews:
            ui.label("No peer reviews yet — be the first to rate this concept.").classes("text-grey-5 italic")
            return
        for review in reviews:
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center gap-2"):
                    score_display(review["score"])
                    ui.label(review["date"].strftime("%d %b %Y")).classes("text-xs text-grey-5 ml-auto")
                if review["comment"]:
                    ui.label(review["comment"]).classes("text-sm text-grey-7 mt-1")

    def submit_review(score_ref: list[int], comment_input: ui.input, review_container: ui.column) -> None:
        score = score_ref[0]
        if score == 0:
            ui.notify("Please select a review score.", type="warning")
            return
        try:
            with SessionLocal() as db:
                ReviewService.submit(db, venture_id, score, comment_input.value or "")
            ui.notify("Review submitted.", type="positive")
            comment_input.set_value("")
            score_ref[0] = 0
            refresh_reviews(review_container)
        except ValueError as err:
            ui.notify(str(err), type="negative")

    def delete_venture() -> None:
        with SessionLocal() as db:
            VentureService.delete(db, venture_id)
        ui.notify("Venture brief deleted.", type="info")
        ui.navigate.to("/")

    with page_layout(data["title"]):
        ui.button("← Back to Explore", on_click=lambda: ui.navigate.to("/")).props("flat size=sm")

        with ui.card().classes("w-full"):
            with ui.row().classes("items-start justify-between w-full flex-wrap gap-4"):
                with ui.column().classes("gap-1"):
                    ui.badge(data["sector"].value, color=sector_color(data["sector"]))
                    ui.label(data["title"]).classes("text-3xl font-bold")
                    ui.label(data["description"]).classes("text-grey-7")
                    if data["author"]:
                        with ui.row().classes("items-center gap-1 mt-1"):
                            ui.icon("person").classes("text-sm text-slate-600")
                            ui.link(f"by {data['author']}", f"/profile/{data['author']}").classes("text-sm text-slate-600 italic")
                    with ui.row().classes("gap-6 mt-2 text-sm text-grey-6"):
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("groups")
                            ui.label(f"Team: {data['team_size']}")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("manage_search")
                            ui.label(f"Discovery: {data['discovery_weeks']} weeks")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("construction")
                            ui.label(f"Build: {data['build_weeks']} weeks")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("timeline")
                            ui.label(f"Total: {data['timeline_weeks']} weeks")

                with ui.column().classes("items-center gap-2"):
                    score_display(data["avg_score"])
                    ui.label(f"{data['avg_score']} / 5.0 ({len(data['reviews'])} reviews)").classes("text-sm text-grey-6")
                    if current_user_id:
                        shortlisted_state: list[bool] = [is_shortlisted]
                        active = ("Shortlisted", "bookmark", "color=dark outline")
                        inactive = ("Shortlist", "bookmark_border", "color=grey-6 outline")
                        label, icon, props = active if is_shortlisted else inactive
                        shortlist_btn = ui.button(label, icon=icon).props(props)

                        def toggle_shortlist() -> None:
                            with SessionLocal() as db:
                                if shortlisted_state[0]:
                                    UserService.remove_shortlist(db, current_user_id, venture_id)
                                    shortlisted_state[0] = False
                                    next_label, next_icon, next_props = inactive
                                    ui.notify("Removed from shortlist.", type="info")
                                else:
                                    UserService.add_shortlist(db, current_user_id, venture_id)
                                    shortlisted_state[0] = True
                                    next_label, next_icon, next_props = active
                                    ui.notify("Added to shortlist.", type="positive")
                            shortlist_btn.set_text(next_label)
                            shortlist_btn.props(f"icon={next_icon} {next_props}")

                        shortlist_btn.on("click", toggle_shortlist)
                    else:
                        ui.button("Login to shortlist", icon="bookmark_border", on_click=lambda: ui.navigate.to("/login")).props("flat color=grey-5 size=sm")

        with ui.row().classes("w-full gap-4 items-start flex-wrap"):
            with ui.card().classes("flex-1 min-w-64"):
                ui.label("Capability Needs").classes("text-xl font-semibold mb-2")
                if data["resource_needs"]:
                    with ui.list().props("dense separator"):
                        for need in data["resource_needs"]:
                            effort = f"{need['effort']:g}" if need["effort"] else ""
                            unit = need["unit"] if need["unit"] else ""
                            label = f"{effort} {unit} {need['name']}".strip()
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.icon("precision_manufacturing").classes("text-slate-500")
                                with ui.item_section():
                                    ui.item_label(label)
                else:
                    ui.label("No capability needs listed.").classes("text-grey-5 italic")

            with ui.card().classes("flex-2 min-w-64"):
                ui.label("Roadmap Milestones").classes("text-xl font-semibold mb-2")
                if data["milestones"]:
                    for idx, milestone in enumerate(data["milestones"], start=1):
                        with ui.row().classes("items-start gap-3 mb-3"):
                            ui.badge(str(idx), color="dark").classes("mt-1 min-w-6 h-6 flex items-center justify-center")
                            ui.label(milestone).classes("text-sm flex-1")
                else:
                    ui.label("No roadmap milestones listed.").classes("text-grey-5 italic")

        with ui.card().classes("w-full"):
            ui.label("Peer Reviews").classes("text-xl font-semibold mb-2")
            review_container = ui.column().classes("w-full gap-2")
            render_reviews(data["reviews"])
            ui.separator()
            ui.label("Leave a review").classes("text-lg font-medium mt-2")
            selected_score: list[int] = [0]
            with ui.row().classes("gap-1 cursor-pointer"):
                star_icons: list[ui.icon] = []

                def make_star_click(i: int):
                    def on_star_click() -> None:
                        selected_score[0] = i
                        for j, icon in enumerate(star_icons, start=1):
                            icon.props("color=amber-7" if j <= i else "color=grey-4")
                    return on_star_click

                for star_i in range(1, 6):
                    icon = ui.icon("star").classes("text-3xl text-grey-4")
                    icon.on("click", make_star_click(star_i))
                    star_icons.append(icon)

            comment_input = ui.input(
                label="Comment (optional)",
                placeholder="What makes this venture promising or risky?",
            ).classes("w-full").props("outlined")
            ui.button(
                "Submit Review",
                icon="send",
                on_click=lambda: submit_review(selected_score, comment_input, review_container),
            ).props("color=dark")

        with ui.expansion("⚠️ Danger Zone", icon="warning").classes("w-full text-red-600"):
            ui.label("Deleting a venture brief is permanent and cannot be undone.").classes("text-sm text-grey-6 mb-2")
            ui.button("Delete this brief", icon="delete", on_click=delete_venture).props("color=negative outline")
