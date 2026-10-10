from functools import wraps

from flask import Flask, abort
from flask_login import LoginManager, current_user

from app_name.models.users import User

login_manager = LoginManager()
login_manager.login_view = "accounts.login"


def init_acl(app: Flask):
    login_manager.init_app(app)


def roles_required(required_roles: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user or not current_user.is_authenticated:
                return login_manager.unauthorized()

            if any(role in current_user.roles for role in required_roles):
                return func(*args, **kwargs)

            abort(403)

        return wrapper

    return decorator


@login_manager.user_loader
def load_user(user_id):
    return User.objects.with_id(user_id)
