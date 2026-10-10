from flask import Blueprint, render_template
from flask_login import login_required

from app_name import models
from app_name.web.caches import cache

module = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@cache.memoize(timeout=60)
def get_summary():
    return {
        "total_users": models.User.objects.count(),
        "active_users": models.User.objects(status="active").count(),
    }


@module.route("")
@login_required
def index():
    return render_template("dashboard/index.html", summary=get_summary())
