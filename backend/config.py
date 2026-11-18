
"""Configuration settings for MathForStudent."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def get_database_url():
    url = os.getenv(
        "DATABASE_URL",
        "sqlite:///mathforstudent.db"
    )

    if url.startswith("postgres://"):
        return url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    if url.startswith("postgresql://"):
        return url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    return url


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-only-change-this-secret"
    )

    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", "10485760")
    )

    UPLOAD_FOLDER = str(
        ROOT_DIR / "instance" / "uploads"
    )

    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "webp"
    }

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower()
        == "true"
    )
