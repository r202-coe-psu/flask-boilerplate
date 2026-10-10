#!/usr/bin/env python3
"""Create (or reset) the first admin user.

Usage: poetry run python scripts/init-admin.py [username]
The generated password is printed once; change it after the first login.
"""

import secrets
import sys

from app_name import models
from app_name.web.config import get_settings


def init_admin(username: str = "admin"):
    password = secrets.token_urlsafe(12)

    user = models.User.objects(username=username).first()
    if not user:
        user = models.User(
            username=username,
            first_name="ผู้ดูแล",
            last_name="ระบบ",
            status="active",
            roles=["admin"],
        )

    user.set_password(password)
    user.is_setup_password = False
    user.save()

    print(f"admin username: {username}")
    print(f"admin password: {password}")


if __name__ == "__main__":
    settings = get_settings()
    models.init_mongoengine(settings)
    print(f"connected to {settings['MONGODB_DB']}")

    init_admin(sys.argv[1] if len(sys.argv) > 1 else "admin")
