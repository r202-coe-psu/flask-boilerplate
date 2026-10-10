import importlib
import logging
import pkgutil

from flask import Blueprint, Flask

from app_name.web.utils import template_filters

logger = logging.getLogger(__name__)


def get_blueprints(package_name: str = __name__) -> list[Blueprint]:
    """Collect `module = Blueprint(...)` from every module under this package.

    Sub-packages are supported: a sub-package's own `module` (in its
    __init__.py) becomes the parent of the blueprints found inside it.
    """
    package = importlib.import_module(package_name)
    blueprints = []

    for info in pkgutil.iter_modules(package.__path__):
        if info.name.startswith("_"):
            continue

        full_name = f"{package_name}.{info.name}"
        try:
            pymod = importlib.import_module(full_name)
        except Exception:
            logger.exception(f"cannot import view module {full_name}")
            raise

        children = get_blueprints(full_name) if info.ispkg else []
        parent = getattr(pymod, "module", None)

        if parent:
            for child in children:
                parent.register_blueprint(child)
            blueprints.append(parent)
        else:
            blueprints.extend(children)

    return blueprints


def register_blueprint(app: Flask):
    for template_filter in template_filters.FILTERS:
        app.add_template_filter(template_filter)

    for blueprint in get_blueprints():
        app.register_blueprint(blueprint)
