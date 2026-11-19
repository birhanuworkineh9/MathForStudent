
"""Authentication API routes for MathForStudent."""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user

from backend.extensions import db, limiter
from backend.models import User
from backend.security.validators import validate_registration
from backend.security.rate_limiter import get_auth_rate_limits


auth_bp = Blueprint("auth", __name__)


def user_response(user):
    """Return safe public user information."""

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "education_level": user.education_level,
    }


@auth_bp.post("/register")
@limiter.limit(get_auth_rate_limits()[0])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request is required.",
        }), 400

    full_name = data.get("full_name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    valid, error = validate_registration(
        full_name,
        email,
        password,
    )

    if not valid:
        return jsonify({
            "status": "error",
            "message": error,
        }), 400

    full_name = full_name.strip()
    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists.",
        }), 409

    user = User(
        full_name=full_name,
        email=email,
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Account registration failed."
        )
        return jsonify({
            "status": "error",
            "message": "Account creation failed. Please try again.",
        }), 500

    return jsonify({
        "status": "success",
        "message": "Account created successfully.",
        "user": user_response(user),
    }), 201


@auth_bp.post("/login")
@limiter.limit(get_auth_rate_limits()[0])
def login():
    if current_user.is_authenticated:
        return jsonify({
            "status": "success",
            "message": "You are already logged in.",
            "user": user_response(current_user),
        }), 200

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request is required.",
        }), 400

    email = data.get("email", "")
    password = data.get("password", "")

    if (
        not isinstance(email, str)
        or not isinstance(password, str)
        or not email.strip()
        or len(password) > 128
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password.",
        }), 400

    user = User.query.filter_by(
        email=email.strip().lower()
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password.",
        }), 401

    login_user(user)

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "user": user_response(user),
    }), 200


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    return jsonify({
        "status": "success",
        "message": "Logged out successfully.",
    }), 200


@auth_bp.get("/me")
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({
            "status": "error",
            "message": "Authentication required.",
        }), 401

    return jsonify({
        "status": "success",
        "user": user_response(current_user),
    }), 200
