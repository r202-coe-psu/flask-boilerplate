# 05 · Forms และ Templates

## Forms (Flask-WTF)

- 1 feature ต่อ 1 ไฟล์ `web/forms/<feature>.py` และต้อง import ใน `web/forms/__init__.py` แล้ว view เรียกผ่าน `forms.<feature>.<FormClass>`
- ทุก form extend `FlaskForm` ซึ่ง validate CSRF ให้อัตโนมัติ
- label เป็นภาษาไทย
- ประกาศ field เองทีละตัว ไม่ใช้ `flask_mongoengine.wtf.model_form` เพราะเป็น deprecated API
- **Search form (GET) ต้องปิด CSRF** ไม่อย่างนั้น `validate()` จะ fail ทุกครั้ง

```python
class SearchProjectForm(FlaskForm):
    class Meta:
        csrf = False

    search = StringField("ค้นหา", [validators.Optional(), validators.Length(max=64)])
```

### `populate_obj`

ใช้ `form.populate_obj(document)` ได้**เฉพาะเมื่อชื่อ field ของ form ตรงกับ field ของ model ทั้งหมด** ถ้า form มี field ที่ต้องจัดการพิเศษ (password, field ที่ไม่ได้อยู่ใน model) ให้ copy ทีละ field ตามแบบใน `users.create_or_edit`

```python
for name in ["username", "first_name", "last_name", "email", "roles"]:
    setattr(user, name, form[name].data)
```

ห้ามให้ form มี field ที่ผู้ใช้ไม่ควรแก้ได้ (เช่น `roles`, `status`, `creator`) ถ้าผู้ใช้คนนั้นไม่มีสิทธิ์แก้ field นั้น

## Layout

ทุกหน้าที่อยู่หลัง login ให้ extend `base/default_page.html` (มี navbar, sidebar, footer และ toast ให้ครบ)

```html
{% extends "base/default_page.html" %}

{% set title_page = "โปรเจกต์" %}
{% set description_page = "รายการโปรเจกต์ทั้งหมด" %}   {# optional #}

{% block back_button %}...{% endblock back_button %}  {# optional #}

{% block content %}
...
{% endblock content %}

{% block js %}...{% endblock js %}                    {# optional: script ประจำหน้า #}
```

หน้าที่ไม่ต้องมี layout (login, error) ให้ extend `base/base.html` แทน

## Macro ที่มีให้ใช้

| Macro | ไฟล์ | ใช้กับ |
|---|---|---|
| `base_render(field, placeholder=...)` | `base/html_renderer.html` | input ทั่วไป (text, email, password, select เดี่ยว) |
| `render_select_field(field)` | `base/html_renderer.html` | select / multi-select |
| `render_text_area_field(field)` | `base/html_renderer.html` | textarea |
| `render_pagination(pagination, endpoint, kwargs={...})` | `components/paginations.html` | pagination ใต้ตาราง |
| `menu_item(endpoint, icon, label, prefix)` | `base/sidebar.html` | เมนูใน sidebar |

```html
{% import "base/html_renderer.html" as renderer %}
{{ renderer.base_render(form.name) }}
{{ renderer.render_text_area_field(form.description) }}
```

ถ้าต้องใช้ UI pattern เดิมซ้ำเกิน 2 หน้า ให้ทำเป็น macro ใน `templates/components/` อย่า copy HTML ซ้ำ

## Flash message

category ที่รองรับมีแค่ 4 ตัว ตรงกับ `components/toasts.html`:

| Category | ใช้เมื่อ |
|---|---|
| `success` | บันทึก/ลบสำเร็จ |
| `error` | ทำไม่สำเร็จ หรือข้อมูลไม่ถูกต้อง |
| `warning` | สำเร็จแต่มีข้อควรระวัง หรืองานยังรอประมวลผล (เช่น job ที่ enqueue ไว้) |
| `info` | แจ้งข้อมูลทั่วไป |

```python
flash("บันทึกโปรเจกต์เรียบร้อยแล้ว", "success")
```

ข้อความเป็นภาษาไทยและเป็นประโยคที่ผู้ใช้อ่านเข้าใจ ห้าม flash `str(exception)` ให้ผู้ใช้เห็น

## CSRF

CSRF เปิดทั้งแอปผ่าน `CSRFProtect` ทุก POST จึงต้องส่ง token มาด้วย:

| ที่มาของ request | วิธีส่ง token |
|---|---|
| Form จาก WTForms | `{{ form.csrf_token }}` หรือ `{{ form.hidden_tag() }}` |
| Form HTML ธรรมดา (เช่นปุ่มลบ) | `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` |
| HTMX | ส่งให้อัตโนมัติผ่าน `hx-headers` บน `<body>` ใน `base/base.html` |
| `fetch()` / jQuery | ใส่ header `X-CSRFToken` เอง |

## HTMX

ใช้ HTMX เพื่อ update บางส่วนของหน้าโดยไม่ต้องเขียน JS เอง pattern มาตรฐานคือ**ค้นหาแบบ live** ตามแบบ `users/index.html`: ให้ request ไปที่ endpoint เดิม แล้วใช้ `hx-select` ตัดเฉพาะส่วนที่ต้องการ ไม่ต้องแยก endpoint partial

```html
<form action="{{ url_for('projects.index') }}" method="get"
  hx-get="{{ url_for('projects.index') }}"
  hx-target="#projects-table" hx-select="#projects-table" hx-swap="outerHTML"
  hx-trigger="input changed delay:400ms from:input, submit"
  hx-push-url="true">
  ...
</form>

<div id="projects-table">...</div>
```

- form ต้องมี `action` และ `method` ปกติด้วย เพื่อให้ยังใช้งานได้แม้ JS ไม่โหลด
- ถ้าต้องแยก partial จริง ๆ ให้ตั้งชื่อไฟล์ขึ้นต้นด้วย `_` เช่น `projects/_table.html` แล้ว `{% include %}` จากหน้าเต็ม
- endpoint ที่ HTMX เรียกต้องมี ACL decorator เหมือน route ปกติ

## Style และ UI

- ใช้ class ของ **DaisyUI** (`btn`, `card`, `table`, `badge`, `alert`, `input`) ก่อน แล้วค่อยเสริมด้วย Tailwind utility
- สีใช้ semantic token (`btn-primary`, `text-error`, `bg-base-200`) ห้าม hardcode hex เพื่อให้เปลี่ยน theme ที่ `static/css/setup.css` ที่เดียวได้
- **ห้าม inline `style="..."`** ถ้าต้องมี class ที่ใช้ซ้ำ ให้เพิ่มใน `setup.css` ด้วย `@apply`
- Icon ใช้ Phosphor: `<i class="ph ph-<name>"></i>` (ดูชื่อ icon ได้ที่ phosphoricons.com) ไม่เพิ่ม icon library อื่น
- ไฟล์ static อ้างอิงผ่าน filter `static_url` ซึ่งเติม query string กัน cache ให้: `{{ 'css/app.css' | static_url }}`
- หลังแก้ template ที่ใช้ class Tailwind ใหม่ ต้อง rebuild CSS: `./scripts/npm run tw` (หรือเปิด `tw:watch` ทิ้งไว้ตอน dev)

## Template filters

| Filter | ตัวอย่าง | ผลลัพธ์ |
|---|---|---|
| `format_date` | `{{ d \| format_date }}` | `10/10/2026` |
| `format_thai_date` | `{{ d \| format_thai_date }}` | `10 ตุลาคม 2569` |
| `format_thai_datetime` | `{{ d \| format_thai_datetime }}` | `10 ต.ค. 2569 14:05 น.` |
| `format_number` | `{{ n \| format_number }}` | `1,234` |
| `static_url` | `{{ 'css/app.css' \| static_url }}` | `/static/css/app.css?date=...` |

ถ้าจะเพิ่ม filter ให้เขียนใน `web/utils/template_filters.py` แล้วเพิ่มลงใน list `FILTERS`
