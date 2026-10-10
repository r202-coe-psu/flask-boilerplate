from app_name.web.config import get_settings

from .server import WorkerServer


def create_server():
    return WorkerServer(get_settings())
