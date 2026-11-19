
"""Rate limiting configuration for MathForStudent."""

from backend.extensions import limiter


DEFAULT_RATE_LIMITS = [
    "200 per day",
    "50 per hour",
]

AUTH_RATE_LIMITS = [
    "10 per hour",
]

QUESTION_RATE_LIMITS = [
    "30 per hour",
]


def get_rate_limiter():
    """Return the shared application limiter."""
    return limiter


def get_default_rate_limits():
    """Return a copy of the default rate limits."""
    return DEFAULT_RATE_LIMITS.copy()


def get_auth_rate_limits():
    """Return authentication endpoint limits."""
    return AUTH_RATE_LIMITS.copy()


def get_question_rate_limits():
    """Return question-solving endpoint limits."""
    return QUESTION_RATE_LIMITS.copy()
