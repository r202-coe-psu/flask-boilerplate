# 09 · ตัวอย่าง Feature ครบชุด (Scaffold)

ตัวอย่างนี้คือ feature `projects` ที่เขียนตาม convention ทุกข้อในเอกสารชุดนี้ เวลาจะเริ่ม feature ใหม่ให้ copy ไปแล้ว **แทนชื่อ** ตามตารางนี้:

| ในตัวอย่าง | แทนด้วย | เช่น |
|---|---|---|
| `projects` | ชื่อ feature (พหูพจน์) | `refugee_camps` |
| `/projects` | url_prefix (kebab-case) | `/refugee-camps` |
| `Project` | ชื่อ model (เอกพจน์) | `RefugeeCamp` |
| `project` / `project_id` | ชื่อตัวแปรเอกพจน์ | `refugee_camp` / `refugee_camp_id` |
| `PROJECT_STATUS_CHOICES` | ชื่อ choices | `REFUGEE_CAMP_STATUS_CHOICES` |

> โค้ดชุดนี้ผ่านการทดสอบจริงบน boilerplate แล้ว (pytest + ruff ผ่าน และเปิดทุกหน้าใน browser ได้)

ผลลัพธ์ที่ได้:

| Method | URL | สิทธิ์ |
|---|---|---|
| GET | `/projects` | login แล้ว |
| GET | `/projects/<project_id>` | login แล้ว |
| GET, POST | `/projects/create`, `/projects/<project_id>/edit` | `admin` |
| POST | `/projects/<project_id>/delete` | `admin` |

---

## 1. Model: `app_name/models/projects.py`

```python
import datetime

import mongoengine as me

PROJECT_STATUS_CHOICES = [
    ("active", "ใช้งาน"),
    ("inactive", "ปิดการใช้งาน"),
]


class Project(me.Document):
    meta = {
        "collection": "projects",
        "indexes": ["name", "status"],
    }

    name = me.StringField(required=True, max_length=255)
    description = me.StringField(default="")

    status = me.StringField(
        required=True,
        default="active",
        choices=[status[0] for status in PROJECT_STATUS_CHOICES],
    )

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    creator = me.ReferenceField("User", dbref=True)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updater = me.ReferenceField("User", dbref=True)

    def display_status(self):
        return dict(PROJECT_STATUS_CHOICES).get(self.status, self.status)
```

แล้วเพิ่มใน `app_name/models/__init__.py`:

```python
from .projects import Project, PROJECT_STATUS_CHOICES

__all__ = [
    # ...ของเดิม
    "Project",
    "PROJECT_STATUS_CHOICES",
]
```

## 2. Form: `app_name/web/forms/projects.py`

```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators


class ProjectForm(FlaskForm):
    name = StringField(
        "ชื่อโปรเจกต์",
        [validators.InputRequired(), validators.Length(max=255)],
    )
    description = TextAreaField("รายละเอียด", [validators.Optional()])


class SearchProjectForm(FlaskForm):
    class Meta:
        csrf = False

    search = StringField("ค้นหา", [validators.Optional(), validators.Length(max=64)])
```

แล้วเพิ่มใน `app_name/web/forms/__init__.py`:

```python
from . import projects

__all__ = [
    # ...ของเดิม
    "projects",
]
```

## 3. View: `app_name/web/views/projects.py`

ไม่ต้อง register เพิ่มที่ไหน เพราะ `get_blueprints()` หาตัวแปร `module` ให้อัตโนมัติ

```python
import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_mongoengine import Pagination

from app_name import models
from app_name.web import forms
from app_name.web.utils.acl import roles_required

module = Blueprint("projects", __name__, url_prefix="/projects")

PER_PAGE = 20


@module.route("")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    form = forms.projects.SearchProjectForm(request.args)

    projects = models.Project.objects(status="active").order_by("-created_date")
    search = (form.search.data or "").strip()
    if search:
        projects = projects.filter(name__icontains=search)

    try:
        pagination = Pagination(projects, page, per_page=PER_PAGE)
    except Exception:
        pagination = Pagination(projects, 1, per_page=PER_PAGE)

    return render_template(
        "projects/index.html",
        projects_pagination=pagination,
        form=form,
        search=search,
    )


@module.route("/<project_id>")
@login_required
def view(project_id):
    project = models.Project.objects.get(id=project_id)
    return render_template("projects/view.html", project=project)


@module.route("/create", methods=["GET", "POST"], defaults={"project_id": None})
@module.route("/<project_id>/edit", methods=["GET", "POST"])
@roles_required(["admin"])
def create_or_edit(project_id):
    project = models.Project()
    if project_id:
        project = models.Project.objects.get(id=project_id)

    form = forms.projects.ProjectForm(obj=project)
    if not form.validate_on_submit():
        return render_template(
            "projects/create_or_edit.html", form=form, project=project
        )

    form.populate_obj(project)
    if not project_id:
        project.creator = current_user._get_current_object()

    project.updater = current_user._get_current_object()
    project.updated_date = datetime.datetime.now()
    project.save()

    flash("บันทึกโปรเจกต์เรียบร้อยแล้ว", "success")
    return redirect(url_for("projects.view", project_id=project.id))


@module.route("/<project_id>/delete", methods=["POST"])
@roles_required(["admin"])
def delete(project_id):
    project = models.Project.objects.get(id=project_id)
    project.status = "inactive"
    project.updater = current_user._get_current_object()
    project.updated_date = datetime.datetime.now()
    project.save()

    flash("ลบโปรเจกต์เรียบร้อยแล้ว", "success")
    return redirect(url_for("projects.index"))
```

จุดที่ควรสังเกต:
- `index` และ `view` ใช้ `@login_required` ส่วนที่เปลี่ยนข้อมูลใช้ `@roles_required(["admin"])` และ decorator อยู่ใต้ `@module.route` เสมอ
- `create_or_edit` ใช้ `populate_obj` ได้ เพราะ field ของ `ProjectForm` ตรงกับ model ทั้งหมด
- ถ้า `project_id` ไม่มีอยู่จริง `objects.get()` จะ raise และได้หน้า 500 ซึ่งเป็นพฤติกรรมที่ทีมยอมรับ (ดู [02-routes-crud.md](02-routes-crud.md) ข้อ 3.3)
- `delete` เป็น soft delete และ `index` กรอง `status="active"`

## 4. Templates

### `app_name/web/templates/projects/index.html`

```html
{% extends "base/default_page.html" %}
{% import "components/paginations.html" as paginations %}

{% set title_page = "โปรเจกต์" %}

{% block content %}
<div class="card bg-base-0 card-body">
  <div class="flex flex-col md:flex-row justify-between gap-4">
    <form action="{{ url_for('projects.index') }}" method="get" class="flex gap-2 w-full md:w-96"
      hx-get="{{ url_for('projects.index') }}" hx-target="#projects-table" hx-select="#projects-table"
      hx-swap="outerHTML" hx-trigger="input changed delay:400ms from:input, submit" hx-push-url="true">
      <label class="input w-full">
        <i class="ph ph-magnifying-glass"></i>
        {{ form.search(placeholder="ค้นหาชื่อโปรเจกต์", class_="grow") }}
      </label>
    </form>
    {% if current_user.is_admin() %}
    <a href="{{ url_for('projects.create_or_edit') }}" class="btn btn-primary">
      <i class="ph ph-plus"></i>
      เพิ่มโปรเจกต์
    </a>
    {% endif %}
  </div>

  <div id="projects-table" class="overflow-x-auto mt-4">
    <table class="table">
      <thead>
        <tr>
          <th>ชื่อโปรเจกต์</th>
          <th>สร้างเมื่อ</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {% for project in projects_pagination.items %}
        <tr>
          <td>
            <a href="{{ url_for('projects.view', project_id=project.id) }}" class="link link-hover">{{ project.name }}</a>
          </td>
          <td>{{ project.created_date | format_thai_datetime }}</td>
          <td class="text-right">
            {% if current_user.is_admin() %}
            <a href="{{ url_for('projects.create_or_edit', project_id=project.id) }}" class="btn btn-ghost btn-sm">
              <i class="ph ph-pencil-simple"></i>
            </a>
            {% endif %}
          </td>
        </tr>
        {% else %}
        <tr>
          <td colspan="3" class="text-center text-base-content/60 py-8">ไม่พบโปรเจกต์</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    {{ paginations.render_pagination(projects_pagination, 'projects.index', kwargs={'search': search}) }}
  </div>
</div>
{% endblock content %}
```

### `app_name/web/templates/projects/view.html`

```html
{% extends "base/default_page.html" %}

{% set title_page = project.name %}

{% block back_button %}
<a href="{{ url_for('projects.index') }}" class="btn btn-ghost btn-sm mb-2">
  <i class="ph ph-arrow-left"></i> กลับ
</a>
{% endblock back_button %}

{% block content %}
<div class="card bg-base-0 card-body max-w-2xl">
  <p class="whitespace-pre-line">{{ project.description or "-" }}</p>
  <p class="text-sm text-base-content/60">
    สร้างเมื่อ {{ project.created_date | format_thai_datetime }}
    {% if project.creator %}โดย {{ project.creator.get_fullname() }}{% endif %}
  </p>

  {% if current_user.is_admin() %}
  <div class="flex justify-end gap-2 pt-4">
    <form method="post" action="{{ url_for('projects.delete', project_id=project.id) }}"
      onsubmit="return confirm('ยืนยันการลบโปรเจกต์นี้?')">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <button class="btn btn-error btn-outline"><i class="ph ph-trash"></i> ลบ</button>
    </form>
    <a href="{{ url_for('projects.create_or_edit', project_id=project.id) }}" class="btn btn-primary">
      <i class="ph ph-pencil-simple"></i> แก้ไข
    </a>
  </div>
  {% endif %}
</div>
{% endblock content %}
```

### `app_name/web/templates/projects/create_or_edit.html`

```html
{% extends "base/default_page.html" %}
{% import "base/html_renderer.html" as renderer %}

{% set title_page = "แก้ไขโปรเจกต์" if project.id else "เพิ่มโปรเจกต์" %}

{% block back_button %}
<a href="{{ url_for('projects.index') }}" class="btn btn-ghost btn-sm mb-2">
  <i class="ph ph-arrow-left"></i> กลับ
</a>
{% endblock back_button %}

{% block content %}
<form method="post" class="card bg-base-0 card-body space-y-2 max-w-2xl">
  {{ form.csrf_token }}

  {{ renderer.base_render(form.name) }}
  {{ renderer.render_text_area_field(form.description) }}

  <div class="flex justify-end gap-2 pt-4">
    <a href="{{ url_for('projects.index') }}" class="btn">ยกเลิก</a>
    <button type="submit" class="btn btn-primary">บันทึก</button>
  </div>
</form>
{% endblock content %}
```

> ปุ่มแก้ไข/ลบถูกซ่อนด้วย `current_user.is_admin()` ซึ่งเป็นแค่ UX ส่วนการป้องกันจริงคือ `@roles_required(["admin"])` ใน view (ดู [03-acl.md](03-acl.md))

## 5. เมนู: `app_name/web/templates/base/sidebar.html`

เพิ่มบรรทัดเดียวใน `<ul class="menu ...">`:

```html
{{ menu_item('projects.index', 'folder', 'โปรเจกต์', '/projects') }}
```

ถ้าเมนูนี้ควรเห็นเฉพาะบาง role ให้ครอบด้วย `{% if current_user.is_admin() %}`

## 6. Test: `tests/test_projects.py`

```python
import pytest

from app_name import models


@pytest.fixture
def user_client(client):
    user = models.User(username="staff", roles=["user"], is_setup_password=True)
    user.set_password("password1234")
    user.save()
    client.post("/login", data={"username": "staff", "password": "password1234"})
    return client


@pytest.fixture
def project(admin):
    return models.Project(name="Demo", creator=admin).save()


def test_index_requires_login(client):
    response = client.get("/projects")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_user_can_list_and_view(user_client, project):
    assert user_client.get("/projects").status_code == 200
    assert user_client.get(f"/projects/{project.id}").status_code == 200


def test_user_cannot_create(user_client):
    response = user_client.post("/projects/create", data={"name": "New"})
    assert response.status_code == 403
    assert models.Project.objects.count() == 0


def test_admin_can_create(admin_client):
    response = admin_client.post(
        "/projects/create", data={"name": "New", "description": "desc"}
    )
    assert response.status_code == 302
    project = models.Project.objects.get(name="New")
    assert project.creator.username == "admin"


def test_admin_can_edit(admin_client, project):
    response = admin_client.post(
        f"/projects/{project.id}/edit", data={"name": "Renamed"}
    )
    assert response.status_code == 302
    project.reload()
    assert project.name == "Renamed"


def test_admin_can_soft_delete(admin_client, project):
    response = admin_client.post(f"/projects/{project.id}/delete")
    assert response.status_code == 302
    project.reload()
    assert project.status == "inactive"
```

## 7. ตรวจผล

```bash
./scripts/npm run tw          # rebuild CSS ให้ class ใหม่ใน template ถูก generate
poetry run pytest tests/test_projects.py
poetry run ruff check . && poetry run ruff format --check .
./scripts/run-web             # เปิด http://localhost:8080/projects
```

