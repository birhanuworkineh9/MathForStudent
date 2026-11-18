
import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.config import Config
from backend.extensions import db, migrate, limiter


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app(config_class=Config):
    """Create and configure the MathForStudent Flask application."""

    app = Flask(__name__)

    # Load application settings
    app.config.from_object(config_class)

    # Ensure required folders exist
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    instance_folder = BASE_DIR / "instance"
    instance_folder.mkdir(parents=True, exist_ok=True)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Import models so SQLAlchemy can register them
    from backend import models  # noqa: F401

    # Register API blueprints
    from backend.routes.questions import questions_bp

    app.register_blueprint(
        questions_bp,
        url_prefix="/api"
    )

    # -----------------------------
    # Frontend routes
    # -----------------------------

    @app.get("/")
    def home():
        return send_from_directory(
            str(FRONTEND_DIR),
            "index.html"
        )

    @app.get("/manifest.json")
    def manifest():
        return send_from_directory(
            str(FRONTEND_DIR),
            "manifest.json"
        )

    @app.get("/service-worker.js")
    def service_worker():
        response = send_from_directory(
            str(FRONTEND_DIR),
            "service-worker.js"
        )

        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"

        return response

    @app.get("/css/<path:filename>")
    def frontend_css(filename):
        return send_from_directory(
            str(FRONTEND_DIR / "css"),
            filename
        )

    @app.get("/js/<path:filename>")
    def frontend_js(filename):
        return send_from_directory(
            str(FRONTEND_DIR / "js"),
            filename
        )

    # -----------------------------
    # API health check
    # -----------------------------

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "success",
            "service": "MathForStudent",
            "message": "Backend is running."
        }), 200

    # -----------------------------
    # Error handlers
    # -----------------------------

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": "error",
            "message": "The request is invalid."
        }), 400

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
            "message": "This request method is not allowed."
        }), 405

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "status": "error",
            "message": "Uploaded file is too large."
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()

        app.logger.exception(
            "An internal server error occurred."
        )

        return jsonify({
            "status": "error",
            "message": "An internal server error occurred. Please try again."
        }), 500

    return app


# -----------------------------
# Run application
# -----------------------------

if __name__ == "__main__":
    application = create_app()

    application.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )


        
        