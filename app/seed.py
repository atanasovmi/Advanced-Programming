"""Populate the database with demo users and sample venture briefs."""

from app.models.database import SessionLocal
from app.models.user import User
from app.models.venture import Sector
from app.services.user_service import UserService
from app.services.venture_service import VentureService

SEED_USERS: list[dict] = [
    {
        "username": "alice",
        "email": "alice@example.com",
        "password": "alice123",
        "bio": "Product strategist who turns early concepts into testable venture stories.",
    },
    {
        "username": "bob",
        "email": "bob@example.com",
        "password": "bob12345",
        "bio": "Operations-minded builder focused on lean launches and scalable delivery.",
    },
]

SEED_VENTURES: list[dict] = [
    {
        "author": "alice",
        "title": "Signal Studio",
        "description": "An AI-assisted insight room that converts interview notes into decision-ready product opportunities.",
        "sector": Sector.AI_DATA,
        "team_size": 4,
        "discovery_weeks": 3,
        "build_weeks": 6,
        "resource_needs": [
            {"name": "User interviews", "effort": 12, "unit": "hours"},
            {"name": "Prompt design", "effort": 16, "unit": "hours"},
            {"name": "Dashboard prototype", "effort": 24, "unit": "hours"},
        ],
        "milestones": [
            "Map the research workflow and define core pain points.",
            "Prototype AI summarisation for three interview formats.",
            "Validate the decision dashboard with two product teams.",
        ],
    },
    {
        "author": "bob",
        "title": "Circular Office Sprint",
        "description": "A workplace reuse marketplace for redistributing surplus furniture, devices, and office materials across campuses.",
        "sector": Sector.SUSTAINABILITY,
        "team_size": 5,
        "discovery_weeks": 2,
        "build_weeks": 5,
        "resource_needs": [
            {"name": "Supplier onboarding", "effort": 10, "unit": "hours"},
            {"name": "Logistics mapping", "effort": 14, "unit": "hours"},
            {"name": "Marketplace UX", "effort": 22, "unit": "hours"},
        ],
        "milestones": [
            "Catalogue reusable inventory categories with pilot partners.",
            "Launch the internal exchange flow for a single office location.",
            "Measure saved cost and avoided waste after the first month.",
        ],
    },
    {
        "author": "alice",
        "title": "Clinic Compass",
        "description": "A patient journey board that coordinates appointment prep, follow-up tasks, and educational reminders.",
        "sector": Sector.HEALTH,
        "team_size": 3,
        "discovery_weeks": 4,
        "build_weeks": 7,
        "resource_needs": [
            {"name": "Workflow interviews", "effort": 18, "unit": "hours"},
            {"name": "Patient messaging design", "effort": 12, "unit": "hours"},
            {"name": "Compliance review", "effort": 8, "unit": "hours"},
        ],
        "milestones": [
            "Document the highest-friction patient touchpoints.",
            "Pilot reminder sequences with one outpatient clinic.",
            "Refine follow-up analytics based on missed-appointment data.",
        ],
    },
    {
        "author": "bob",
        "title": "Studio Class Loop",
        "description": "A creative academy portal that turns workshop ideas into repeatable learning programs with live mentor feedback.",
        "sector": Sector.EDUCATION,
        "team_size": 4,
        "discovery_weeks": 3,
        "build_weeks": 4,
        "resource_needs": [
            {"name": "Curriculum design", "effort": 20, "unit": "hours"},
            {"name": "Mentor recruitment", "effort": 10, "unit": "hours"},
            {"name": "Demo content production", "effort": 15, "unit": "hours"},
        ],
        "milestones": [
            "Define the first three workshop tracks and target outcomes.",
            "Create mentor dashboards for feedback and attendance.",
            "Open the pilot cohort and measure completion quality.",
        ],
    },
    {
        "author": "alice",
        "title": "City Storyline",
        "description": "A cultural discovery platform that links local venues, hidden histories, and themed walking experiences.",
        "sector": Sector.CULTURE,
        "team_size": 3,
        "discovery_weeks": 2,
        "build_weeks": 6,
        "resource_needs": [
            {"name": "Archive research", "effort": 14, "unit": "hours"},
            {"name": "Route curation", "effort": 12, "unit": "hours"},
            {"name": "Mobile interaction design", "effort": 18, "unit": "hours"},
        ],
        "milestones": [
            "Curate the first story route with three venue partners.",
            "Prototype map-driven audio interactions on mobile.",
            "Test the guided route with local visitors and students.",
        ],
    },
    {
        "author": "bob",
        "title": "Focus Flow Desk",
        "description": "A lightweight operations cockpit for managers who want daily priorities, blockers, and follow-ups in one place.",
        "sector": Sector.PRODUCTIVITY,
        "team_size": 4,
        "discovery_weeks": 2,
        "build_weeks": 5,
        "resource_needs": [
            {"name": "Process mapping", "effort": 10, "unit": "hours"},
            {"name": "Automation rules", "effort": 14, "unit": "hours"},
            {"name": "Executive dashboard", "effort": 20, "unit": "hours"},
        ],
        "milestones": [
            "Identify the key signals managers need each morning.",
            "Launch blocker tracking and follow-up automation.",
            "Review adoption metrics with the pilot operations team.",
        ],
    },
]


def seed_database() -> None:
    """Insert demo users and sample venture briefs when the database is empty."""
    with SessionLocal() as db:
        if VentureService.get_all(db):
            return

        user_map: dict[str, int] = {}
        for entry in SEED_USERS:
            existing_user = db.query(User).filter(User.username == entry["username"]).first()
            if existing_user:
                user_map[entry["username"]] = existing_user.id
                continue
            user = UserService.register(
                db,
                username=entry["username"],
                email=entry["email"],
                password=entry["password"],
                bio=entry["bio"],
            )
            user_map[entry["username"]] = user.id

        for venture_data in SEED_VENTURES:
            VentureService.create(
                db=db,
                title=venture_data["title"],
                description=venture_data["description"],
                sector=venture_data["sector"],
                team_size=venture_data["team_size"],
                discovery_weeks=venture_data["discovery_weeks"],
                build_weeks=venture_data["build_weeks"],
                resource_needs=venture_data["resource_needs"],
                milestones=venture_data["milestones"],
                user_id=user_map.get(venture_data.get("author")),
            )

    print(
        f"Database seeded with {len(SEED_USERS)} demo users and "
        f"{len(SEED_VENTURES)} sample ventures."
    )
