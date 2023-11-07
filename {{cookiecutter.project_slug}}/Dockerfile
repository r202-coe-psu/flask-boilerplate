FROM python:3-bookworm
# RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
# RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update --fix-missing && apt dist-upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales nodejs
RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG th_TH.UTF-8 
ENV LANGUAGE th_TH:en 
ENV LC_ALL th_TH.UTF-8


RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn

WORKDIR /app

ENV {{ cookiecutter.project_slug.upper() }}_SETTINGS=/app/.prod.env

COPY poetry.lock pyproject.toml /app/
RUN $PYTHON -m poetry config virtualenvs.create false && $PYTHON -m poetry install --no-interaction --only main

COPY {{ cookiecutter.project_slug }}/web/static/package.json app/web/static/
RUN npm install --prefix app/web/static

COPY {{ cookiecutter.project_slug }}/web/static/src/main.css app/web/static/
COPY . /app

RUN npm --prefix app/web/static run tw:prod

ENV PYTHONPATH $(pwd):/usr/lib/python3/site-packages:$PYTHONPATH