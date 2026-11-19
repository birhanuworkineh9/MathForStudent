
"""Rate limiting helpers for MathForStudent.

This module reuses the shared limiter defined in
backend.extensions. Do not create a second Limiter instance.
"""

from backend.extensions import limiter


# Default limits to use when configuring the shared limiter.
DEFAULT_RATE_LIMITS = [
    "200 per day",
    "50 per hour",
]


def get_rate_limiter():
    """Return the application's shared rate limiter."""
    return limiter


def get_default_rate_limits():
    """Return a copy of the default request limits."""
    return DEFAULT_RATE_LIMITS.copy()

