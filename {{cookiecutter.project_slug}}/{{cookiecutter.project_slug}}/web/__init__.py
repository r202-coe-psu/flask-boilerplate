from flask import Flask

from .. import models
from . import views
from . import acl
from . import oauth2

app = Flask(__name__)


def create_app():
    app.config.from_object("{{ cookiecutter.project_slug }}.config")
    app.config.from_envvar(
        "{{ cookiecutter.project_slug.upper() }}_SETTINGS", silent=True
    )

    models.init_db(app)
    views.register_blueprint(app)
    acl.init_acl(app)
    oauth2.init_oauth(app)

    return app
