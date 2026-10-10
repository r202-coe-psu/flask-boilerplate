# --- Build CSS ---
FROM node:22-slim AS assets

WORKDIR /app/app_name/web/static
COPY app_name/web/static/package.json app_name/web/static/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY app_name/web/templates /app/app_name/web/templates
COPY app_name/web/static/css ./css
RUN npm run tw:minify && npm prune --omit=dev


# --- Runtime ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_REQUESTS_TIMEOUT=400

RUN apt-get update \
    && apt-get install -y --no-install-recommends locales \
    && sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=th_TH.UTF-8 \
    LANGUAGE=th_TH:en

RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --no-interaction --only main --no-root

COPY . .
RUN poetry install --no-interaction --only main

COPY --from=assets /app/app_name/web/static/css/app.css app_name/web/static/css/app.css
COPY --from=assets /app/app_name/web/static/node_modules app_name/web/static/node_modules

RUN useradd --create-home --uid 1000 app && chown -R app /app
USER app

EXPOSE 8080
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8080", "app_name.web:create_app()"]
