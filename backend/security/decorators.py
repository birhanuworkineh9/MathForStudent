
"""Authentication and authorization decorators for MathForStudent."""

from functools import wraps

from flask import jsonify
from flask_login import current_user


def login_required_api(function):
    """Require an authenticated user for an API endpoint."""

    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                "status": "error",
                "message": "Please log in to continue.",
            }), 401

        return function(*args, **kwargs)

    return decorated_function


def admin_required(function):
    """Require an authenticated administrator."""

    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                "status": "error",
                "message": "Authentication required.",
            }), 401

        if not getattr(current_user, "is_admin", False):
            return jsonify({
                "status": "error",
                "message": "Administrator permission required.",
            }), 403

        return function(*args, **kwargs)

    return decorated_function

