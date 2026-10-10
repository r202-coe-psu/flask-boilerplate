"""OAuth2 / OpenID Connect login via Authlib.

Each provider listed in LOGIN_PROVIDERS is registered by name. Authlib reads
its settings from config keys prefixed with the upper-cased name, e.g.

    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_SERVER_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
    GOOGLE_CLIENT_KWARGS={"scope": "openid email profile"}

To support a provider whose user info differs from OIDC, add a function to
USERINFO_MAPPERS that converts it to the common shape used by get_or_create_user().
"""

import datetime

from authlib.integrations.flask_client import OAuth
from flask import redirect, session, url_for
from flask_login import login_user

from app_name import models

oauth2_client = OAuth()


def map_oidc_userinfo(user_info: dict) -> dict:
    return {
        "username": user_info.get("email"),
        "email": user_info.get("email"),
        "first_name": user_info.get("given_name", ""),
        "last_name": user_info.get("family_name", ""),
    }


USERINFO_MAPPERS = {
    "google": map_oidc_userinfo,
}


def get_user_info(remote, token) -> dict:
    user_info = token.get("userinfo")
    if not user_info:
        user_info = remote.userinfo(token=token)
    return dict(user_info)


def get_or_create_user(info: dict) -> models.User:
    user = None
    if info.get("email"):
        user = models.User.objects(email=info["email"]).first()
    if not user and info.get("username"):
        user = models.User.objects(username=info["username"]).first()

    if not user:
        user = models.User(
            username=info.get("username") or info.get("email"),
            email=info.get("email"),
            first_name=(info.get("first_name") or "").title(),
            last_name=(info.get("last_name") or "").title(),
            status="active",
            roles=["user"],
            # OAuth users do not need a local password
            is_setup_password=True,
        )
        user.save()

    return user


def handle_authorized_oauth2(remote, token):
    user_info = get_user_info(remote, token)
    mapper = USERINFO_MAPPERS.get(remote.name, map_oidc_userinfo)
    user = get_or_create_user(mapper(user_info))

    if not login_user(user):
        return redirect(url_for("accounts.login", error="บัญชีนี้ถูกปิดการใช้งาน"))

    user.resources[remote.name] = user_info
    user.last_login_date = datetime.datetime.now()
    user.save()

    expires_at = token.get("expires_at")
    models.OAuth2Token.objects(name=remote.name, user=user).update_one(
        set__token_type=token.get("token_type"),
        set__access_token=token.get("access_token"),
        set__refresh_token=token.get("refresh_token"),
        set__expires=(
            datetime.datetime.fromtimestamp(expires_at)
            if expires_at
            else datetime.datetime.now()
        ),
        upsert=True,
    )

    next_uri = session.pop("next", None)
    return redirect(next_uri or url_for("index.index"))


def init_oauth(app):
    oauth2_client.init_app(app)
    for name in app.config.get("LOGIN_PROVIDERS", []):
        oauth2_client.register(name)
