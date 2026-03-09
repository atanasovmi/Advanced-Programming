"""Page for creating a new venture brief with dynamic capability and milestone rows."""

from nicegui import ui

from app.models.database import SessionLocal
from app.models.venture import Sector
from app.services.venture_service import VentureService
from app.views.auth import get_current_user_id, get_current_username
from app.views.shared import page_layout


@ui.page("/submit")
def add_venture_page() -> None:
    """Render the venture submission form."""
    current_user_id = get_current_user_id()
    current_username = get_current_username()

    resource_rows: list[dict] = []
    milestone_rows: list[ui.textarea] = []

    resource_container: ui.column
    milestone_container: ui.column

    def add_resource_row() -> None:
        with resource_container:
            row_ref: dict = {}
            with ui.row().classes("w-full gap-2 items-center") as row_el:
                row_ref["name"] = ui.input(placeholder="e.g. UX research").classes("flex-2").props("outlined dense")
                row_ref["effort"] = ui.number(placeholder="12", min=0).classes("w-24").props("outlined dense")
                row_ref["unit"] = ui.input(placeholder="hours").classes("w-24").props("outlined dense")

                def remove() -> None:
                    if row_ref in resource_rows:
                        resource_rows.remove(row_ref)
                    row_el.delete()

                ui.button(icon="remove_circle_outline", on_click=remove).props("flat round color=red-4 dense")
            resource_rows.append(row_ref)

    def add_milestone_row() -> None:
        milestone_number = len(milestone_rows) + 1
        with milestone_container:
            with ui.row().classes("w-full gap-2 items-start") as row_el:
                ui.badge(str(milestone_number), color="dark").classes("mt-2 min-w-6 h-6 flex items-center justify-center")
                milestone_input = ui.textarea(
                    placeholder=f"Milestone {milestone_number}: describe the expected outcome..."
                ).classes("flex-1").props("outlined dense autogrow")

                def remove() -> None:
                    if milestone_input in milestone_rows:
                        milestone_rows.remove(milestone_input)
                    row_el.delete()

                ui.button(icon="remove_circle_outline", on_click=remove).props("flat round color=red-4 dense")
            milestone_rows.append(milestone_input)

    def submit_form(
        title_input: ui.input,
        desc_input: ui.textarea,
        sector_select,
        team_size_input: ui.number,
        discovery_input: ui.number,
        build_input: ui.number,
    ) -> None:
        resource_needs = []
        for row in resource_rows:
            name = (row["name"].value or "").strip()
            if not name:
                continue
            resource_needs.append(
                {
                    "name": name,
                    "effort": row["effort"].value or 0,
                    "unit": (row["unit"].value or "").strip(),
                }
            )

        milestones = [
            (entry.value or "").strip()
            for entry in milestone_rows
            if (entry.value or "").strip()
        ]

        try:
            with SessionLocal() as db:
                venture = VentureService.create(
                    db=db,
                    title=title_input.value or "",
                    description=desc_input.value or "",
                    sector=Sector(sector_select.value),
                    team_size=int(team_size_input.value or 3),
                    discovery_weeks=int(discovery_input.value or 0),
                    build_weeks=int(build_input.value or 0),
                    resource_needs=resource_needs,
                    milestones=milestones,
                    user_id=current_user_id,
                )
            ui.notify(f"'{venture.title}' saved successfully.", type="positive")
            ui.navigate.to(f"/venture/{venture.id}")
        except ValueError as err:
            ui.notify(str(err), type="negative")

    with page_layout("Submit Venture — VentureCanvas"):
        ui.label("Submit a Venture Brief").classes("text-3xl font-bold")

        if current_username:
            with ui.row().classes("items-center gap-1 text-sm text-slate-700"):
                ui.icon("account_circle").classes("text-sm")
                ui.label("This brief will be attributed to:")
                ui.label(current_username).classes("font-semibold")
        else:
            with ui.row().classes(
                "items-center gap-2 bg-amber-50 border border-amber-300 rounded p-3 text-sm text-amber-800"
            ):
                ui.icon("info").classes("text-amber-600")
                ui.label(
                    "You are submitting as a guest. Log in to connect the venture to your public profile."
                )
                ui.button("Login", icon="login", on_click=lambda: ui.navigate.to("/login")).props("flat color=amber-8 dense size=sm")

        ui.button("← Back to Explore", on_click=lambda: ui.navigate.to("/")).props("flat size=sm")

        with ui.card().classes("w-full"):
            ui.label("Brief Overview").classes("text-lg font-semibold mb-2")
            with ui.column().classes("w-full gap-3"):
                title_input = ui.input(
                    label="Venture Title *",
                    placeholder="e.g. Signal Studio",
                ).classes("w-full").props("outlined")
                desc_input = ui.textarea(
                    label="Strategic Summary",
                    placeholder="Describe the problem, audience, and the opportunity this venture addresses...",
                ).classes("w-full").props("outlined autogrow")
                with ui.row().classes("w-full gap-3 flex-wrap"):
                    sector_select = ui.select(
                        label="Sector *",
                        options={sector.value: sector.value for sector in Sector},
                        value=Sector.PRODUCTIVITY.value,
                    ).classes("flex-1 min-w-40").props("outlined")
                    team_size_input = ui.number(label="Team Size", value=3, min=1).classes("w-28").props("outlined")
                    discovery_input = ui.number(label="Discovery (weeks)", value=0, min=0).classes("w-36").props("outlined")
                    build_input = ui.number(label="Build (weeks)", value=0, min=0).classes("w-36").props("outlined")

        with ui.card().classes("w-full"):
            ui.label("Capability Needs").classes("text-lg font-semibold")
            ui.label("Capability · Effort · Unit (e.g. UX research · 12 · hours)").classes("text-xs text-grey-5 mb-2")
            resource_container = ui.column().classes("w-full gap-2")
            add_resource_row()
            add_resource_row()
            add_resource_row()
            ui.button("Add Capability", icon="add", on_click=add_resource_row).props("outline color=dark size=sm")

        with ui.card().classes("w-full"):
            ui.label("Roadmap Milestones").classes("text-lg font-semibold mb-2")
            milestone_container = ui.column().classes("w-full gap-2")
            add_milestone_row()
            add_milestone_row()
            ui.button("Add Milestone", icon="add", on_click=add_milestone_row).props("outline color=dark size=sm")

        ui.button(
            "💾 Save Venture Brief",
            on_click=lambda: submit_form(
                title_input,
                desc_input,
                sector_select,
                team_size_input,
                discovery_input,
                build_input,
            ),
        ).props("color=dark size=lg").classes("self-end")
