from flask import Blueprint, current_app

module = Blueprint("api", __name__, url_prefix="/api")


@module.route("/healthz")
def healthz():
    return {"status": "ok", "version": current_app.config.get("VERSION")}
