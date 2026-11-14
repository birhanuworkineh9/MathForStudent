from flask import Blueprint, request, jsonify, session
from backend.extensions import db
from backend.models import User
from backend.security.validation import validate_registration

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    valid, error = validate_registration(
        full_name,
        email,
        password
    )

    if not valid:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists."
        }), 409

    user = User(
        full_name=full_name,
        email=email
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "status": "success",
        "message": "Account created successfully."
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }
    })


@auth_bp.post("/logout")
def logout():
    session.clear()

    return jsonify({
        "status": "success",
        "message": "Logged out successfully."
    })


@auth_bp.get("/me")
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Authentication required."
        }), 401

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({
            "status": "error",
            "message": "User not found."
        }), 404

    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "education_level": user.education_level
        }
    })

    