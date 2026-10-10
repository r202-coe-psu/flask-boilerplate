import ast
import os
import pathlib
import logging

import flask
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

SETTINGS_ENVVAR = "APP_SETTINGS"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]

settings = None


def _parse_value(key: str, value: str):
    if value is None:
        return value

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    if "CLIENT_KWARGS" in key:
        return ast.literal_eval(value)

    if key == "LOGIN_PROVIDERS":
        return [p.strip() for p in value.split(",") if p.strip()]

    if value.isdigit():
        return int(value)

    return value


def load_config(config: flask.Config) -> flask.Config:
    """Load settings in order: default_settings -> .env file -> environment.

    The .env path defaults to <project root>/.env and can be overridden with
    $APP_SETTINGS.
    """
    config.from_object("app_name.default_settings")

    env_file = os.environ.get(SETTINGS_ENVVAR, str(PROJECT_ROOT / ".env"))
    logger.debug(f"settings file: {env_file}")

    values = dotenv_values(env_file)
    config.update({k: _parse_value(k, v) for k, v in values.items()})

    # Environment variables win over the file (e.g. MONGODB_HOST in docker-compose)
    for key in list(config.keys()):
        if key in os.environ:
            config[key] = _parse_value(key, os.environ[key])

    # Keep cache pointing at the same Redis unless explicitly overridden
    if "CACHE_REDIS_URL" not in values and "CACHE_REDIS_URL" not in os.environ:
        config["CACHE_REDIS_URL"] = config["REDIS_URL"]

    return config


def get_settings() -> flask.Config:
    """Settings for processes without a Flask app (e.g. the RQ worker)."""
    global settings

    if not settings:
        settings = load_config(flask.Config(str(PROJECT_ROOT)))

    return settings
