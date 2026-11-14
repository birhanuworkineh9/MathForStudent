
import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, migrate, limiter


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    # Create upload directory
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Import models so SQLAlchemy can register them
    from backend import models

    # CORS configuration
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    # Register API routes
    from backend.routes.questions import questions_bp

    app.register_blueprint(
        questions_bp,
        url_prefix="/api"
    )

    # Frontend directory
    frontend_dir = (
        Path(__file__).resolve().parent.parent / "frontend"
    )

    # Main frontend page
    @app.get("/")
    def home():
        return send_from_directory(
            frontend_dir,
            "index.html"
        )

    # PWA manifest
    @app.get("/manifest.json")
    def manifest():
        return send_from_directory(
            frontend_dir,
            "manifest.json"
        )

    # Service worker
    @app.get("/service-worker.js")
    def service_worker():
        return send_from_directory(
            frontend_dir,
            "service-worker.js"
        )

    # Frontend CSS
    @app.get("/css/<path:filename>")
    def frontend_css(filename):
        return send_from_directory(
            frontend_dir / "css",
            filename
        )

    # Frontend JavaScript
    @app.get("/js/<path:filename>")
    def frontend_js(filename):
        return send_from_directory(
            frontend_dir / "js",
            filename
        )

    # API health check
    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "success",
            "service": "MathForStudent"
        })

    # 404 error handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    # File size error handler
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "status": "error",
            "message": "Uploaded file is too large."
        }), 413

    return app


if __name__ == "__main__":
    application = create_app()

    application.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

    

