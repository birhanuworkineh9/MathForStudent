from flask import Flask

from .config import Config
from .extensions import (
    db,
    migrate,
    login_manager,
    limiter
)


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Load logged-in user from database
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User

        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # Register application routes
    from .routes.auth import auth_bp
    from .routes.questions import questions_bp
    from .routes.ai_tutor import ai_tutor_bp
    from .routes.progress import progress_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(ai_tutor_bp)
    app.register_blueprint(progress_bp)

    @app.route("/")
    def home():
        return {
            "app": "MathForStudent",
            "status": "running"
        }

    return app
  
