import os
from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, migrate, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}}
    )

    from backend.routes.questions import questions_bp
    app.register_blueprint(questions_bp, url_prefix="/api")

    @app.get("/")
    def home():
        return jsonify({
            "app": "MathForStudent",
            "status": "running",
            "message": "MathForStudent API is ready."
        })

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "success",
            "service": "MathForStudent"
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "status": "error",
            "message": "Uploaded file is too large."
        }), 413

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=False)
    

