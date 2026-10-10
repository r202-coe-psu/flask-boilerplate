VERSION = "0.1.0"
APP_TITLE = "App Name"
SECRET_KEY = "changethisonproduction"

MONGODB_DB = "app_name_db"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017

REDIS_URL = "redis://localhost:6379"

# Comma separated in .env, e.g. LOGIN_PROVIDERS="google,psu"
LOGIN_PROVIDERS = ["google"]

# SimpleCache is per-process; use RedisCache when running multiple gunicorn workers.
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 300
