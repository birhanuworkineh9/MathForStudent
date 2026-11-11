import re

from flask import Blueprint, request, jsonify
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from ..extensions import db
from ..models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


def valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def user_response(user):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "education_level": user.education_level
    }


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    level = str(
        data.get("education_level", "Grade 9")
    ).strip()

    if not full_name or not email or not password:
        return jsonify({
            "error": "All required fields must be provided."
        }), 400

    if len(full_name) > 120:
        return jsonify({
            "error": "Full name is too long."
        }), 400

    if len(email) > 254 or not valid_email(email):
        return jsonify({
            "error": "Enter a valid email address."
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters."
        }), 400

    allowed_levels = [
        "Grade 9",
        "Grade 10",
        "Grade 11",
        "Grade 12",
        "University",
        "Self-Learner"
    ]

    if level not in allowed_levels:
        return jsonify({
            "error": "Invalid education level."
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "This email is already registered."
        }), 409

    user = User(
        full_name=full_name,
        email=email,
        education_level=level
    )

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        login_user(user)

        return jsonify({
            "message": "Account created successfully.",
            "user": user_response(user)
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "error": "Account creation failed."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str) or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Incorrect email or password."
        }), 401

    login_user(user)

    return jsonify({
        "message": "Login successful.",
        "user": user_response(user)
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    return jsonify({
        "message": "Logout successful."
    }), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "user": user_response(current_user)
    }), 200
