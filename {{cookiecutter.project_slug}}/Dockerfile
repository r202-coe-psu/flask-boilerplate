FROM debian:sid
# RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free non-free-firmware' > /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales
# RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
# ENV LANG th_TH.UTF-8 
# ENV LANGUAGE th_TH:en 
# ENV LC_ALL th_TH.UTF-8


ENV {{ cookiecutter.project_slug.upper() }}_SETTINGS=/app/{{ cookiecutter.project_slug }}-production.cfg

RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3

RUN $PYTHON -m pip install poetry

WORKDIR /app
COPY {{ cookiecutter.project_slug }}/cmd /app/{{ cookiecutter.project_slug }}/cmd
COPY poetry.lock pyproject.toml README.md /app/
RUN $PYTHON -m poetry config virtualenvs.create false && $PYTHON -m poetry install --no-interaction --only main

COPY {{ cookiecutter.project_slug }}/web/static/package.json {{ cookiecutter.project_slug }}/web/static/package-lock.json {{ cookiecutter.project_slug }}/web/static/
RUN npm install --prefix {{ cookiecutter.project_slug }}/web/static

COPY . /app



# RUN ln -s $(command -v python3) /usr/bin/python
# RUN pip3 install poetry
# RUN poetry config virtualenvs.create false && poetry install --no-interaction

# For brython
# RUN cd /app/{{ cookiecutter.project_slug }}/web/static/brython; \
#     for i in $(ls -d */); \
#     do \
#     cd $i; \
#     python3 -m brython --make_package ${i%%/}; \
#     mv *.brython.js ..; \
#     cd ..; \
#     done
