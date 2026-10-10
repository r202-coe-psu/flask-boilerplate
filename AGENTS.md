# AGENTS.md

Instructions for AI coding agents working in this repository. The full guideline (in Thai) lives in `docs/`; read the relevant file before writing code.

## Stack

Flask 3 · MongoEngine · Flask-Login · Flask-WTF (CSRF on) · Flask-Caching (Redis) · RQ · Authlib · Jinja2 + Tailwind v4/DaisyUI 5 + HTMX · Poetry · pytest + mongomock · ruff

## Commands

```bash
poetry run pytest                 # tests (no real MongoDB needed)
poetry run ruff check . && poetry run ruff format --check .
./scripts/npm run tw              # rebuild CSS after using new Tailwind classes
./scripts/run-web                 # dev server on :8080
```

## Rules

1. **Every route must have an ACL decorator** placed _below_ `@module.route(...)`:
   `@login_required` (from `flask_login`) or `@roles_required(["role"])` (from `app_name.web.utils.acl`, takes a **list**).
   Intentionally public routes need a `# public: <reason>` comment. Never gate pages with `if role in current_user.roles`; in-view checks are only for record ownership. → `docs/03-acl.md`
2. **CRUD naming**: `web/views/<plural>.py` with `module = Blueprint("<plural>", __name__, url_prefix="/<plural-kebab>")`; functions `index`, `view`, `create_or_edit`, `delete`; URL param `<singular>_id`; templates `templates/<plural>/{index,view,create_or_edit}.html`. → `docs/02-routes-crud.md`
3. Mutations are **POST only** with a CSRF token, then `flash(...)` + `redirect(...)`.
4. Fetch by id with `Model.objects.get(id=...)`.
5. **Soft delete** (`status = "inactive"`); set `creator`/`updater`/`updated_date` manually in views.
6. New models go in `models/<plural>.py` with explicit `meta["collection"]` and must be exported from `models/__init__.py`. → `docs/04-models.md`
7. Forms: one file per feature in `web/forms/`, registered in `web/forms/__init__.py`; search forms disable CSRF. Do not use `model_form`. → `docs/05-forms-templates.md`
8. Long-running work goes to `worker/tasks.py` via `redis_queue.enqueue`, passing ids rather than documents. → `docs/06-jobs-cache-config.md`
9. Every feature needs tests: not logged in → 302 to login, wrong role → 403, plus CRUD happy paths. → `docs/07-testing.md`
10. New config keys go in both `default_settings.py` and `.env.example`; never commit secrets or `.env`.

## Language

- Code, identifiers, code comments: **English**.
- UI text (labels, flash messages): **Thai**.
- `docs/`: **Thai**.
- Commit messages: `<type>: <summary>` (`feat|fix|hotfix|refactor|style|docs|test|chore`). → `docs/08-git-workflow.md`

When adding a feature, start from `docs/09-feature-scaffold.md`.
