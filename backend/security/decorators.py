
"""
MathForStudent Security Decorators

Provides reusable authentication and authorization decorators.
"""

from functools import wraps

from flask import jsonify
from flask_login import current_user


def login_required_api(function):
    """Require a logged-in student to access an API endpoint."""

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:
            return jsonify({
                "status": "error",
                "message": "Please log in to continue."
            }), 401

        return function(*args, **kwargs)

    return decorated_function


def admin_required(function):
    """Restrict an endpoint to authorized administrators."""

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:
            return jsonify({
                "status": "error",
                "message": "Authentication required."
            }), 401

        if not getattr(current_user, "is_admin", False):
            return jsonify({
                "status": "error",
                "message": "Administrator permission required."
            }), 403

        return function(*args, **kwargs)

    return decorated_function
