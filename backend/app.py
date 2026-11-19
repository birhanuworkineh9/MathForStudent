
"""Application factory and HTTP routes for MathForStudent."""

from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.config import Config
from backend.extensions import db, limiter, migrate
from backend.security.authentication import configure_authentication


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app(config_class=Config):
    """Create and configure the MathForStudent application."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Create required application directories.
    Path(app.instance_path).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(app.config["UPLOAD_FOLDER"]).mkdir(
        parents=True,
        exist_ok=True
    )

    # Initialize shared Flask extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Import models so SQLAlchemy can register them.
    from backend import models  # noqa: F401

    # Configure user authentication and session loading.
    configure_authentication(app)

    # Import API blueprints.
    from backend.routes.auth import auth_bp
    from backend.routes.questions import questions_bp
    from backend.routes.progress import progress_bp

    # Register API routes.
    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        questions_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        progress_bp,
        url_prefix="/api/progress"
    )

    # Frontend home page.
    @app.get("/")
    def home():
        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    # PWA files.
    @app.get("/manifest.json")
    def manifest():
        return send_from_directory(
            FRONTEND_DIR,
            "manifest.json"
        )

    @app.get("/service-worker.js")
    def service_worker():
        response = send_from_directory(
            FRONTEND_DIR,
            "service-worker.js"
        )
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    # Search engine files.
    @app.get("/robots.txt")
    def robots():
        return send_from_directory(
            FRONTEND_DIR,
            "robots.txt"
        )

    @app.get("/sitemap.xml")
    def sitemap():
        return send_from_directory(
            FRONTEND_DIR,
            "sitemap.xml"
        )

    # Frontend CSS and JavaScript.
    @app.get("/css/<path:filename>")
    def frontend_css(filename):
        return send_from_directory(
            FRONTEND_DIR / "css",
            filename
        )

    @app.get("/js/<path:filename>")
    def frontend_js(filename):
        return send_from_directory(
            FRONTEND_DIR / "js",
            filename
        )

    # Backend health check.
    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "success",
            "service": "MathForStudent",
            "message": "Backend is running."
        }), 200

    # HTTP error handlers.
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "status": "error",
            "message": "HTTP method not allowed."
        }), 405

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "status": "error",
            "message": "Uploaded file is too large."
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.exception(
            "Unhandled application error"
        )

        return jsonify({
            "status": "error",
            "message": "An internal application error occurred."
        }), 500

    return app


if __name__ == "__main__":
    application = create_app()

    application.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )




