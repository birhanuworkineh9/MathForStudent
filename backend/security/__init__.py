
"""
MathForStudent Security Package
"""

from functools import wraps

from flask import jsonify
from flask_login import current_user


def authenticated_user_required(function):
    """
    Protect a route so only authenticated users can access it.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:
            return jsonify({
                "status": "error",
                "message": "Authentication required."
            }), 401

        return function(*args, **kwargs)

    return decorated_function
