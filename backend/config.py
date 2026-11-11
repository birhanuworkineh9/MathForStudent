"""
MathForStudent Configuration

Supports local development and production deployment.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Application security
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        SECRET_KEY = "local-development-only-change-this-key"

    # Database configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///mathforstudent.db"
    )

    # Normalize PostgreSQL URLs for psycopg 3
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # AI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

    # Upload configuration
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "uploads"
    )

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
    )

    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Request protection
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def validate(cls):
        if not os.getenv("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY must be configured in production."
            )

        if not os.getenv("DATABASE_URL"):
            raise RuntimeError(
                "DATABASE_URL must be configured in production."
  )
  
