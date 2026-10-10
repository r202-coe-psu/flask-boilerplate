import mongoengine as me
from flask import Flask
from flask_mongoengine import MongoEngine

from .users import User, USER_ROLES
from .oauth2 import OAuth2Token

__all__ = [
    "User",
    "USER_ROLES",
    "OAuth2Token",
]

db = MongoEngine()


def init_db(app: Flask):
    app.config.setdefault(
        "MONGODB_SETTINGS",
        {
            "db": app.config.get("MONGODB_DB"),
            "host": app.config.get("MONGODB_HOST", "localhost"),
            "port": int(app.config.get("MONGODB_PORT", 27017)),
            "username": app.config.get("MONGODB_USERNAME") or None,
            "password": app.config.get("MONGODB_PASSWORD") or None,
        },
    )
    db.init_app(app)


def init_mongoengine(settings):
    """Connect outside of a Flask app context (e.g. RQ worker, scripts)."""
    me.connect(
        db=settings.get("MONGODB_DB"),
        host=settings.get("MONGODB_HOST", "localhost"),
        port=int(settings.get("MONGODB_PORT", 27017)),
        username=settings.get("MONGODB_USERNAME") or None,
        password=settings.get("MONGODB_PASSWORD") or None,
    )
