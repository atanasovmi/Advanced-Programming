"""Resource planner page that aggregates capability needs across venture briefs."""

from nicegui import ui

from app.models.database import SessionLocal
from app.services.venture_service import VentureService
from app.views.shared import page_layout


@ui.page("/planner")
def resource_planner_page() -> None:
    """Render the resource planner page."""
    with SessionLocal() as db:
        all_ventures = [
            {"id": venture.id, "title": venture.title}
            for venture in VentureService.get_all(db)
        ]

    selected_ids: set[int] = set()

    def generate(result_container: ui.column) -> None:
        result_container.clear()
        if not selected_ids:
            with result_container:
                ui.label("Please select at least one venture brief.").classes("text-warning")
            return

        aggregated: dict[tuple[str, str], dict] = {}
        with SessionLocal() as db:
            for venture_id in selected_ids:
                venture = VentureService.get_by_id(db, venture_id)
                if venture is None:
                    continue
                for need in venture.resource_needs:
                    key = (need.name.lower(), need.unit.lower())
                    if key in aggregated:
                        aggregated[key]["effort"] += need.effort
                    else:
                        aggregated[key] = {
                            "name": need.name,
                            "effort": need.effort,
                            "unit": need.unit,
                        }

        with result_container:
            if not aggregated:
                ui.label("The selected ventures do not list any capability needs.").classes("text-grey-5 italic")
                return
            ui.label(f"Resource Plan ({len(aggregated)} lines)").classes("text-xl font-semibold")
            ui.button("🖨️ Print / Save as PDF", on_click=lambda: ui.run_javascript("window.print()")).props("outline color=grey-7 size=sm")
            with ui.list().props("dense separator").classes("w-full"):
                for item in sorted(aggregated.values(), key=lambda x: x["name"]):
                    effort = f"{item['effort']:g}" if item["effort"] else ""
                    unit = item["unit"] if item["unit"] else ""
                    label = f"{item['name']} — {effort} {unit}".strip(" —")
                    with ui.item():
                        with ui.item_section().props("avatar"):
                            ui.icon("assignment_turned_in").classes("text-slate-500")
                        with ui.item_section():
                            ui.item_label(label)

    with page_layout("Resource Planner — VentureCanvas"):
        ui.label("Resource Planner").classes("text-3xl font-bold")
        ui.label(
            "Select multiple venture briefs and aggregate their capability needs into one planning view."
        ).classes("text-grey-6")

        with ui.row().classes("w-full gap-4 items-start flex-wrap"):
            with ui.card().classes("flex-1 min-w-64"):
                ui.label("Select Venture Briefs").classes("text-lg font-semibold mb-2")
                if not all_ventures:
                    ui.label("No venture briefs are available yet.").classes("text-grey-5 italic")
                else:
                    for venture_data in all_ventures:
                        venture_id = venture_data["id"]

                        def make_toggle(selected_id: int):
                            def toggle(e) -> None:
                                if e.value:
                                    selected_ids.add(selected_id)
                                else:
                                    selected_ids.discard(selected_id)
                            return toggle

                        ui.checkbox(venture_data["title"], on_change=make_toggle(venture_id))

            with ui.card().classes("flex-2 min-w-72"):
                result_container = ui.column().classes("w-full gap-2")
                with result_container:
                    ui.label("Your aggregated resource plan will appear here.").classes("text-grey-5 italic")

        if all_ventures:
            ui.button(
                "Generate Plan",
                icon="rule_folder",
                on_click=lambda: generate(result_container),
            ).props("color=dark")
