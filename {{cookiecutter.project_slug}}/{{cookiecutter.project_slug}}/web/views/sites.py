from flask import Blueprint, render_template
from {{ cookiecutter.project_slug }}.web.forms.users import LoginForm

module = Blueprint("site", __name__)


@module.route("/")
def index():
    login_form = LoginForm()
    if not login_form.validate_on_submit():
        print(login_form.errors)
        return render_template("site/index.html", login_form=login_form)
    return render_template("site/index.html", login_form=login_form)
