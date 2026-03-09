"""
app/views/auth.py

Login ("/login") and Register ("/register") pages.

Session state is stored in NiceGUI's per-browser ``app.storage.user``
dict, keyed by ``'user_id'`` and ``'username'``.  This dict is backed
by an encrypted cookie so the session survives page reloads.

Helper functions:
    get_current_user_id()  → int | None
    get_current_username() → str | None
    login_user(user)       → None  (writes to storage)
    logout_user()          → None  (clears storage)
"""

from nicegui import ui, app as _app

from app.models.database import SessionLocal
from app.services.user_service import UserService
from app.views.shared import page_layout


# ---------------------------------------------------------------------------
# Session helpers (imported by other views)
# ---------------------------------------------------------------------------

def get_current_user_id() -> int | None:
    """Return the logged-in user's id, or None if not authenticated."""
    return _app.storage.user.get("user_id")


def get_current_username() -> str | None:
    """Return the logged-in user's username, or None if not authenticated."""
    return _app.storage.user.get("username")


def login_user(user) -> None:
    """Persist the user's session after a successful login."""
    _app.storage.user["user_id"]  = user.id
    _app.storage.user["username"] = user.username


def logout_user() -> None:
    """Clear the current user's session."""
    _app.storage.user.pop("user_id",  None)
    _app.storage.user.pop("username", None)


# ---------------------------------------------------------------------------
# /login
# ---------------------------------------------------------------------------

@ui.page("/login")
def login_page() -> None:
    """Render the login form."""

    # If already logged in, send straight to profile
    if get_current_user_id():
        ui.navigate.to("/profile")
        return

    with page_layout("Login — RecipeVault"):
        with ui.card().classes("w-full max-w-md mx-auto"):
            ui.label("Sign in to RecipeVault").classes(
                "text-2xl font-bold text-center mb-4"
            )

            username_input = ui.input(
                label="Username", placeholder="your_username"
            ).classes("w-full").props("outlined")

            password_input = ui.input(
                label="Password", password=True, password_toggle_button=True
            ).classes("w-full").props("outlined")

            def do_login() -> None:
                username = (username_input.value or "").strip()
                password = password_input.value or ""
                if not username or not password:
                    ui.notify("Please fill in both fields.", type="warning")
                    return
                with SessionLocal() as db:
                    user = UserService.authenticate(db, username, password)
                if user is None:
                    ui.notify(
                        "Invalid username or password.", type="negative"
                    )
                    return
                login_user(user)
                ui.notify(f"Welcome back, {user.username}! 👋", type="positive")
                ui.navigate.to("/")

            ui.button(
                "Sign In", icon="login", on_click=do_login
            ).props("color=teal size=lg").classes("w-full mt-2")

            ui.separator().classes("my-3")

            with ui.row().classes("justify-center gap-1 text-sm"):
                ui.label("Don't have an account?").classes("text-grey-6")
                ui.link("Register here", "/register").classes(
                    "text-teal-600 font-medium"
                )


# ---------------------------------------------------------------------------
# /register
# ---------------------------------------------------------------------------

@ui.page("/register")
def register_page() -> None:
    """Render the registration form."""

    if get_current_user_id():
        ui.navigate.to("/profile")
        return

    with page_layout("Register — RecipeVault"):
        with ui.card().classes("w-full max-w-md mx-auto"):
            ui.label("Create your account").classes(
                "text-2xl font-bold text-center mb-4"
            )

            username_input = ui.input(
                label="Username *",
                placeholder="e.g. pasta_lover_42",
            ).classes("w-full").props("outlined")
            ui.label(
                "3–80 chars · letters, digits, underscores only"
            ).classes("text-xs text-grey-5 -mt-2")

            email_input = ui.input(
                label="Email address *",
                placeholder="you@example.com",
            ).classes("w-full").props("outlined")

            password_input = ui.input(
                label="Password *  (min 6 characters)",
                password=True,
                password_toggle_button=True,
            ).classes("w-full").props("outlined")

            bio_input = ui.textarea(
                label="Short bio (optional)",
                placeholder="Tell the community a little about yourself …",
            ).classes("w-full").props("outlined autogrow")

            def do_register() -> None:
                try:
                    with SessionLocal() as db:
                        user = UserService.register(
                            db,
                            username=username_input.value or "",
                            email=email_input.value or "",
                            password=password_input.value or "",
                            bio=bio_input.value or "",
                        )
                    login_user(user)
                    ui.notify(
                        f"Account created! Welcome, {user.username}! 🎉",
                        type="positive",
                    )
                    ui.navigate.to("/")
                except ValueError as err:
                    ui.notify(str(err), type="negative")

            ui.button(
                "Create Account", icon="person_add", on_click=do_register
            ).props("color=teal size=lg").classes("w-full mt-2")

            ui.separator().classes("my-3")

            with ui.row().classes("justify-center gap-1 text-sm"):
                ui.label("Already have an account?").classes("text-grey-6")
                ui.link("Sign in", "/login").classes(
                    "text-teal-600 font-medium"
                )


# ---------------------------------------------------------------------------
# /logout  (navigable URL for convenience)
# ---------------------------------------------------------------------------

@ui.page("/logout")
def logout_page() -> None:
    """Log out the current user and redirect to the home page."""
    logout_user()
    ui.navigate.to("/")
