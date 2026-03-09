"""Home page that lists all venture briefs with search and sector filters."""

from nicegui import ui

from app.models.database import SessionLocal
from app.models.venture import Sector
from app.services.venture_service import VentureService
from app.views.shared import page_layout, score_display, sector_color


@ui.page("/")
def home_page() -> None:
    """Render the VentureCanvas home page."""
    search_query: list[str] = [""]
    active_sector: list[str] = ["all"]

    def render_ventures(container: ui.column) -> None:
        container.clear()
        with SessionLocal() as db:
            ventures = (
                VentureService.search(db, search_query[0])
                if search_query[0]
                else VentureService.get_all(db)
            )
            if active_sector[0] != "all":
                selected = Sector(active_sector[0])
                ventures = [venture for venture in ventures if venture.sector == selected]
            cards_data = [
                {
                    "id": venture.id,
                    "title": venture.title,
                    "description": venture.description,
                    "sector": venture.sector,
                    "team_size": venture.team_size,
                    "timeline_weeks": venture.timeline_weeks,
                    "avg_score": round(venture.average_score, 1),
                    "num_reviews": len(venture.reviews),
                    "author": venture.author.username if venture.author else None,
                }
                for venture in ventures
            ]

        with container:
            if not cards_data:
                ui.label("No venture briefs match your current filter.").classes(
                    "text-grey-5 text-xl text-center w-full mt-10"
                )
                return
            with ui.grid(columns=3).classes("w-full gap-4"):
                for data in cards_data:
                    _venture_card(data)

    def _venture_card(data: dict) -> None:
        with ui.card().classes(
            "cursor-pointer hover:shadow-lg transition-shadow w-full"
        ).on("click", lambda d=data: ui.navigate.to(f"/venture/{d['id']}")):
            ui.badge(data["sector"].value, color=sector_color(data["sector"])).classes("text-xs")
            ui.label(data["title"]).classes("text-lg font-bold mt-1")
            ui.label(data["description"]).classes("text-sm text-grey-6 line-clamp-2")
            if data["author"]:
                ui.label(f"by {data['author']}").classes("text-xs text-slate-600 italic")
            with ui.row().classes("items-center justify-between mt-2 w-full"):
                with ui.row().classes("items-center gap-1"):
                    score_display(data["avg_score"])
                    ui.label(f"({data['num_reviews']})").classes("text-xs text-grey-5")
                with ui.row().classes("items-center gap-3 text-xs text-grey-6"):
                    ui.icon("groups").classes("text-sm")
                    ui.label(f"{data['team_size']} people")
                    ui.icon("schedule").classes("text-sm")
                    ui.label(f"{data['timeline_weeks']} weeks")

    with page_layout("Explore — VentureCanvas"):
        ui.label("Explore Venture Briefs").classes("text-3xl font-bold")
        ui.label(
            "Browse innovation concepts, compare their timelines, and shortlist the ideas worth developing next."
        ).classes("text-grey-6")

        def on_search(e) -> None:
            search_query[0] = e.value.strip()
            render_ventures(venture_grid)

        ui.input(
            placeholder="Search ventures by title or description…",
            on_change=on_search,
        ).classes("w-full").props("outlined clearable")

        with ui.row().classes("gap-2 flex-wrap"):
            def make_filter(label: str, value: str) -> None:
                def activate() -> None:
                    active_sector[0] = value
                    render_ventures(venture_grid)

                ui.chip(label, on_click=activate).props("outline clickable").classes("capitalize")

            make_filter("All", "all")
            for sector in Sector:
                make_filter(sector.value, sector.value)

        venture_grid = ui.column().classes("w-full")
        render_ventures(venture_grid)
