
"""Authentication configuration for MathForStudent."""

from flask import Flask
from flask_login import LoginManager

from backend.extensions import db, login_manager
from backend.models import User


def configure_authentication(app: Flask) -> None:
    """Initialize Flask-Login and configure user loading."""

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id: str):
        """Load a user from the database using the session ID."""

        try:
            user_id_number = int(user_id)
        except (TypeError, ValueError):
            return None

        return db.session.get(User, user_id_number)
