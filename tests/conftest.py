import os

import mongomock
import pytest
from mongoengine.connection import get_db

# Do not pick up a developer's local .env during tests
os.environ["APP_SETTINGS"] = os.devnull

from app_name import models  # noqa: E402
from app_name.web import create_app  # noqa: E402


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "WTF_CSRF_ENABLED": False,
            "CACHE_TYPE": "NullCache",
            "LOGIN_PROVIDERS": [],
            "MONGODB_SETTINGS": {
                "db": "test",
                "host": "mongodb://localhost",
                "mongo_client_class": mongomock.MongoClient,
            },
        }
    )
    yield app

    # Start every test with an empty database
    db = get_db()
    for name in db.list_collection_names():
        db.drop_collection(name)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    user = models.User(username="admin", roles=["admin"], is_setup_password=True)
    user.set_password("password1234")
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin):
    client.post("/login", data={"username": "admin", "password": "password1234"})
    return client
