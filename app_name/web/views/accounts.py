import datetime
import logging
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app_name import models
from app_name.web import forms, oauth2

logger = logging.getLogger(__name__)

module = Blueprint("accounts", __name__)


def is_safe_next_url(target: str | None) -> bool:
    if not target:
        return False
    parts = urlsplit(target)
    return not parts.scheme and not parts.netloc and target.startswith("/")


@module.route("/login", methods=["GET", "POST"])
def login():
    form = forms.accounts.LoginForm()
    error_msg = request.args.get("error")
    next_url = request.args.get("next")

    if not form.validate_on_submit():
        if is_safe_next_url(next_url):
            session["next"] = next_url
        return render_template("accounts/login.html", form=form, error_msg=error_msg)

    user = models.User.objects(username=form.username.data).first()
    if not user or not user.check_password(form.password.data):
        error_msg = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
        return render_template("accounts/login.html", form=form, error_msg=error_msg)

    if not login_user(user):
        error_msg = "บัญชีนี้ถูกปิดการใช้งาน"
        return render_template("accounts/login.html", form=form, error_msg=error_msg)

    user.last_login_date = datetime.datetime.now()
    user.save()

    if not user.is_setup_password:
        return redirect(url_for("accounts.setup_password"))

    next_url = session.pop("next", None)
    return redirect(next_url if is_safe_next_url(next_url) else url_for("index.index"))


@module.route("/login/<name>")
def login_oauth(name):
    if name not in current_app.config.get("LOGIN_PROVIDERS", []):
        abort(404)

    remote = oauth2.oauth2_client.create_client(name)
    scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
    redirect_uri = url_for(
        "accounts.authorized_oauth", name=name, _external=True, _scheme=scheme
    )
    return remote.authorize_redirect(redirect_uri)


@module.route("/auth/<name>")
def authorized_oauth(name):
    if name not in current_app.config.get("LOGIN_PROVIDERS", []):
        abort(404)

    remote = oauth2.oauth2_client.create_client(name)
    try:
        token = remote.authorize_access_token()
    except Exception:
        logger.exception(f"cannot authorize access token from {name}")
        return redirect(url_for("accounts.login", error="เข้าสู่ระบบไม่สำเร็จ"))

    session["oauth_provider"] = name
    return oauth2.handle_authorized_oauth2(remote, token)


@module.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index.index"))


@module.route("/setup-password", methods=["GET", "POST"])
@login_required
def setup_password():
    form = forms.accounts.SetupPasswordForm()
    if not form.validate_on_submit():
        return render_template("accounts/setup-password.html", form=form)

    current_user.set_password(form.password.data)
    current_user.is_setup_password = True
    current_user.save()
    flash("ตั้งค่ารหัสผ่านเรียบร้อยแล้ว", "success")
    return redirect(url_for("index.index"))
