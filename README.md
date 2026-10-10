# Flask App Template

Starter for server-rendered Flask projects:

- **Backend:** Flask 3, MongoEngine (`flask-mongoengine-3`), Flask-Login, Flask-WTF (CSRF on by default), Flask-Caching (Redis), Authlib (OAuth2/OIDC)
- **Background jobs:** RQ + Redis
- **Frontend:** Jinja2, Tailwind CSS v4 + DaisyUI 5, HTMX, jQuery, Phosphor Icons
- **Runtime:** gunicorn, Docker / docker-compose (MongoDB, Redis, web, worker)

## Start a new project from this template

Rename the package and identifiers (replace `myproject` with your project name):

```bash
git mv app_name myproject
grep -rlI --exclude-dir={.git,.venv,node_modules} -e app_name -e app-name . \
  | xargs sed -i 's/app_name/myproject/g; s/app-name/myproject/g'
```

Then set `APP_TITLE` in `.env` and adjust the DaisyUI theme in
`myproject/web/static/css/setup.css`.

## Development

```bash
cp .env.example .env
poetry install
./scripts/npm install
./scripts/npm run tw:watch      # rebuild CSS on change
docker compose up -d mongodb redis
poetry run python scripts/init-admin.py   # prints a generated admin password
./scripts/run-web               # http://localhost:8080
./scripts/run-worker            # RQ worker
```

Tests and lint:

```bash
poetry run pytest
poetry run ruff check .
```

## Production

```bash
docker compose up -d --build
```

## Project layout

```
app_name/
├── default_settings.py     # config defaults (overridden by .env, then env vars)
├── cmd/                    # CLI entrypoints: app-web, app-worker
├── models/                 # MongoEngine documents
├── worker/                 # RQ worker server + tasks.py
└── web/
    ├── __init__.py         # create_app() factory
    ├── config.py           # settings loader shared by web and worker
    ├── caches.py           # Flask-Caching
    ├── redis_rq.py         # RQ queue wrapper
    ├── oauth2.py           # Authlib providers from LOGIN_PROVIDERS
    ├── forms/              # Flask-WTF forms, one module per feature
    ├── views/              # blueprints, auto-registered
    ├── utils/              # acl, error handling, template filters
    ├── templates/          # base layout, components, pages
    └── static/             # npm project: Tailwind entry, built app.css
```

## Conventions

- **Configuration** is loaded in this order: `default_settings.py` → `.env`
  (path overridable with `APP_SETTINGS`) → environment variables.
- **Views:** add `web/views/<feature>.py` with a `module = Blueprint(...)`. It is
  registered automatically, with no import list to update.
- **CRUD feature:** `views/<feature>.py` + `forms/<feature>.py` +
  `templates/<feature>/{index,create_or_edit}.html`.
- **Authorization:** use `@login_required`, or `@roles_required(["admin"])` from
  `web/utils/acl.py`.
- **Background jobs:** write functions in `worker/tasks.py` and enqueue them with
  `redis_queue.enqueue(tasks.fn, ...)`. Jobs run without a Flask app context.
- **OAuth login:** list providers in `LOGIN_PROVIDERS` and set
  `<NAME>_CLIENT_ID`, `<NAME>_CLIENT_SECRET`, and `<NAME>_SERVER_METADATA_URL`.
  Non-OIDC providers need a mapper in `web/oauth2.py:USERINFO_MAPPERS`.
