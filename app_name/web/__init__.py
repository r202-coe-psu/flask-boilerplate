import optparse

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from . import views
from .. import models
from . import redis_rq
from . import oauth2
from . import caches
from .config import load_config
from .utils import acl
from .utils.error_handling import init_error_handling

csrf = CSRFProtect()


def create_app(config: dict | None = None):
    app = Flask(__name__)
    load_config(app.config)
    if config:
        app.config.update(config)

    csrf.init_app(app)
    views.register_blueprint(app)
    caches.init_cache(app)
    models.init_db(app)
    acl.init_acl(app)
    redis_rq.init_rq(app)
    oauth2.init_oauth(app)
    init_error_handling(app)

    return app


def get_program_options(default_host="127.0.0.1", default_port="8080"):
    parser = optparse.OptionParser()
    parser.add_option(
        "-H",
        "--host",
        help="Hostname of the Flask app " + "[default %s]" % default_host,
        default=default_host,
    )
    parser.add_option(
        "-P",
        "--port",
        help="Port for the Flask app " + "[default %s]" % default_port,
        default=default_port,
    )

    # Useful for debugging, but not exposed in the help message.
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug", help=optparse.SUPPRESS_HELP
    )
    parser.add_option(
        "-p",
        "--profile",
        action="store_true",
        dest="profile",
        help=optparse.SUPPRESS_HELP,
    )

    options, _ = parser.parse_args()
    return options
