import os

from pathlib import Path
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)
from dotenv import load_dotenv

from backend.services.ai_service import solve_with_ai


BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

load_dotenv(BASE_DIR / ".env")


app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "MathForStudent backend is running."
    })


@app.route("/api/solve", methods=["POST"])
def solve():

    question = request.form.get(
        "question", ""
    ).strip()

    subject = request.form.get(
        "subject", ""
    ).strip()

    education_level = request.form.get(
        "education_level", ""
    ).strip()

    photo = request.files.get("photo")

    if not question and not photo:

        return jsonify({
            "error": "Please enter a question or upload an image."
        }), 400

    allowed_subjects = [
        "Mathematics",
        "Physics",
        "Chemistry",
        "Computer Science"
    ]

    if subject not in allowed_subjects:

        return jsonify({
            "error": "Please select a valid subject."
        }), 400

    if not education_level:

        return jsonify({
            "error": "Please select your education level."
        }), 400

    if photo:

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if photo.mimetype not in allowed_types:

            return jsonify({
                "error": "Please upload a JPEG, PNG or WebP image."
            }), 400

    try:

        answer = solve_with_ai(
            question=question,
            subject=subject,
            education_level=education_level,
            image=photo
        )

        return jsonify({
            "status": "success",
            "answer": answer,
            "subject": subject,
            "education_level": education_level
        }), 200

    except Exception:

        app.logger.exception(
            "Question solving failed."
        )

        return jsonify({
            "error": (
                "Unable to solve your question. "
                "Please check the server configuration "
                "and try again."
            )
        }), 500


@app.errorhandler(413)
def file_too_large(error):

    return jsonify({
        "error": "Uploaded file is too large. Maximum size is 10 MB."
    }), 413


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

