"""
MathForStudent Rate Limiting Security

Helps protect API endpoints from excessive requests.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_limiter(app=None):
    """Create and optionally initialize the rate limiter."""

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    if app is not None:
        limiter.init_app(app)

    return limiter
  
