# 02 · Route และ CRUD Convention

เอกสารนี้กำหนดวิธีตั้งชื่อและวิธีเขียน route ของทุก feature ทุกตัวอย่างใช้ feature สมมติชื่อ `projects` และต้นแบบจริงในโค้ดดูได้ที่ `app_name/web/views/users.py`

## 1. การตั้งชื่อ

| สิ่งที่ตั้งชื่อ   | Convention                                                                                                | ตัวอย่าง                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| ชื่อ feature      | **พหูพจน์**, snake_case                                                                                   | `projects`, `refugee_camps`              |
| ไฟล์ view         | `web/views/<feature>.py`                                                                                  | `web/views/projects.py`                  |
| ตัวแปร Blueprint  | ต้องชื่อ **`module`** เท่านั้น                                                                            | `module = Blueprint(...)`                |
| ชื่อ Blueprint    | เท่ากับชื่อ feature                                                                                       | `Blueprint("projects", __name__, ...)`   |
| `url_prefix`      | `/` + ชื่อ feature แบบ kebab-case                                                                         | `/projects`, `/refugee-camps`            |
| URL parameter     | `<<เอกพจน์>_id>`                                                                                          | `<project_id>`                           |
| Model             | **เอกพจน์**, PascalCase                                                                                   | `Project` ใน `models/projects.py`        |
| Form              | `<Model>Form`, `Search<Model>Form` (ถ้า create กับ edit ต่างกัน: `Create<Model>Form` / `Edit<Model>Form`) | `ProjectForm` ใน `web/forms/projects.py` |
| โฟลเดอร์ template | `templates/<feature>/`                                                                                    | `templates/projects/`                    |
| ตัวแปรใน template | instance เดียวใช้เอกพจน์ (`project`) ส่วน pagination ใช้ `<feature>_pagination`                           | `projects_pagination`                    |

> **ทำไมต้องชื่อ `module`:** `web/views/__init__.py:get_blueprints()` ไล่ import ทุกไฟล์ใน `web/views/` แล้วหยิบตัวแปรที่ชื่อ `module` ไป register ให้อัตโนมัติ ถ้าตั้งชื่ออื่น route จะไม่ถูก register และจะไม่มี error เตือนเลย

## 2. Route มาตรฐานของ CRUD

| Method    | URL                             | Function         | Endpoint (`url_for`)      | Template                       |
| --------- | ------------------------------- | ---------------- | ------------------------- | ------------------------------ |
| GET       | `/projects`                     | `index`          | `projects.index`          | `projects/index.html`          |
| GET       | `/projects/<project_id>`        | `view`           | `projects.view`           | `projects/view.html`           |
| GET, POST | `/projects/create`              | `create_or_edit` | `projects.create_or_edit` | `projects/create_or_edit.html` |
| GET, POST | `/projects/<project_id>/edit`   | `create_or_edit` | `projects.create_or_edit` | `projects/create_or_edit.html` |
| POST      | `/projects/<project_id>/delete` | `delete`         | `projects.delete`         | (redirect)                     |

ถ้ามี action อื่นที่ไม่ใช่ CRUD ให้ตั้งเป็น `POST /<feature>/<id>/<verb>` และตั้งชื่อ function เป็น verb นั้น เช่น `POST /users/<user_id>/deactivate` ใช้ function `deactivate`

### โครงของ view file

```python
module = Blueprint("projects", __name__, url_prefix="/projects")

PER_PAGE = 20


@module.route("")
@login_required
def index(): ...


@module.route("/<project_id>")
@login_required
def view(project_id): ...


@module.route("/create", methods=["GET", "POST"], defaults={"project_id": None})
@module.route("/<project_id>/edit", methods=["GET", "POST"])
@roles_required(["admin"])
def create_or_edit(project_id): ...


@module.route("/<project_id>/delete", methods=["POST"])
@roles_required(["admin"])
def delete(project_id): ...
```

ให้เรียง function ตามลำดับนี้เสมอ: `index → view → create_or_edit → delete → action อื่น ๆ`

## 3. กฎการเขียน route

### 3.1 ห้ามเปลี่ยนข้อมูลด้วย GET

ทุกอย่างที่เขียนลง DB (create, update, delete, ส่งอีเมล, enqueue job) ต้องเป็น `POST` เพราะ GET ถูก browser, crawler หรือ link preview เรียกซ้ำเองได้ และไม่มี CSRF protection

```html
{# ❌ ผิด #}
<a href="{{ url_for('projects.delete', project_id=project.id) }}">ลบ</a>

{# ✅ ถูก #}
<form
  method="post"
  action="{{ url_for('projects.delete', project_id=project.id) }}"
>
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
  <button class="btn btn-error">ลบ</button>
</form>
```

### 3.2 POST สำเร็จแล้วต้อง flash และ redirect (Post/Redirect/Get)

ห้าม `render_template` หลังบันทึกสำเร็จ เพราะถ้าผู้ใช้กด refresh form จะถูกส่งซ้ำ

```python
project.save()
flash("บันทึกโปรเจกต์เรียบร้อยแล้ว", "success")
return redirect(url_for("projects.view", project_id=project.id))
```

ถ้า validate ไม่ผ่าน ให้ `render_template` ฟอร์มเดิมกลับไปพร้อม error (ไม่ redirect)

### 3.3 ดึง document ด้วย `objects.get(...)`

```python
project = models.Project.objects.get(id=project_id)
```

ถ้าไม่พบ document หรือ id ผิด format, MongoEngine จะ raise `DoesNotExist` / `ValidationError` และผู้ใช้จะเห็นหน้า 500 ซึ่ง**ยอมรับได้ตามข้อตกลงของทีม** ไม่ต้องห่อ try/except ทุกที่

### 3.4 `create_or_edit` ใช้ function เดียวและ template เดียว

แยกโหมดด้วย `<x>_id` ว่าเป็น `None` หรือไม่ (ผ่าน `defaults={"project_id": None}`) ใน template ให้เช็ก `project.id` เพื่อสลับหัวข้อ "เพิ่ม/แก้ไข"

### 3.5 List ต้องมี pagination

ใช้ `flask_mongoengine.Pagination` และค่าคงที่ `PER_PAGE` ประจำไฟล์ ถ้าเลขหน้าเกินจำนวนหน้าที่มี ให้ fallback ไปหน้า 1 ตามแบบใน `users.index` ห้าม `.all()` หรือ `list(Model.objects)` มา render ทั้ง collection

### 3.6 Query string สำหรับค้นหา

ใช้ `Search<Model>Form(request.args)` ที่ปิด CSRF (`class Meta: csrf = False`) แล้วส่ง `search` กลับไปให้ template ใช้ใน `render_pagination(..., kwargs={'search': search})` เพื่อให้คำค้นยังอยู่ตอนเปลี่ยนหน้า

### 3.7 อ้างอิง URL ด้วย `url_for` เสมอ

ห้าม hardcode path ใน Python และ template ให้ใช้ `url_for("projects.view", project_id=...)` แทน `"/projects/" + id`

### 3.8 Soft delete

`delete` ไม่ลบ document จริง ให้ตั้ง `status = "inactive"` พร้อม `updater` และ `updated_date` แล้ว query ใน `index` ต้องกรอง `status="active"`

### 3.9 Route ที่คืน JSON

ให้ไปไว้ใน `web/views/api.py` (prefix `/api`) หรือสร้าง blueprint `api_<feature>` ที่มี prefix `/api/<feature>` ไม่ผสม route HTML กับ JSON ไว้ใน blueprint เดียวกัน ยกเว้น partial HTML สำหรับ HTMX

### 3.10 Business logic ที่ยาว

ถ้า logic ใน view ยาวเกิน 30–40 บรรทัด หรือถูกเรียกจากหลายที่ (view, worker, script) ให้แยกไปเป็น function ใน `app_name/services/<feature>.py` แล้วให้ view ทำแค่ อ่าน input → เรียก service → render/redirect

## 4. Checklist ก่อนเปิด PR (route)

- [ ] ไฟล์ `web/views/<feature>.py` ตัวแปรชื่อ `module`
- [ ] URL, function และ template ตรงตามตารางในข้อ 2
- [ ] ทุก route มี ACL decorator ตาม [03-acl.md](03-acl.md)
- [ ] ทุก action ที่เปลี่ยนข้อมูลเป็น POST และมี CSRF token
- [ ] POST สำเร็จแล้ว flash + redirect
- [ ] List มี pagination
- [ ] Delete เป็น soft delete
