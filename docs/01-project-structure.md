# 01 · โครงสร้างโปรเจกต์

## ภาพรวม

```
Browser ──► gunicorn ──► Flask app (create_app)
                           ├─ Blueprints   (web/views/*)
                           ├─ Flask-Login  + ACL decorators (web/utils/acl.py)
                           ├─ Flask-WTF    (CSRF ทั้งแอป)
                           ├─ Flask-Caching (Redis)
                           └─ Authlib      (OAuth2 / OIDC)
                                 │
                 ┌───────────────┼────────────────┐
                 ▼               ▼                ▼
              MongoDB          Redis ◄──── RQ worker (worker/*)
           (MongoEngine)   (cache + queue)
```

Web กับ worker ใช้ codebase เดียวกัน ต่างกันแค่ entrypoint ใน `app_name/cmd/`

## โครงไฟล์

```
app_name/
├── default_settings.py        # ค่า default ของ config ทุกตัว
├── cmd/
│   ├── web.py                 # entrypoint: app-web (dev server)
│   └── worker.py              # entrypoint: app-worker (RQ worker)
├── models/                    # MongoEngine Document, 1 ไฟล์ต่อ 1 domain
│   ├── __init__.py            # export model + init_db() / init_mongoengine()
│   ├── users.py
│   └── oauth2.py
├── worker/
│   ├── server.py              # RQ worker (connect DB เอง เพราะไม่มี Flask app)
│   └── tasks.py               # function ที่ถูก enqueue
└── web/
    ├── __init__.py            # create_app(): app factory
    ├── config.py              # load_config(): โหลด config ให้ทั้ง web และ worker
    ├── caches.py              # cache = Cache()
    ├── redis_rq.py            # redis_queue.enqueue(...)
    ├── oauth2.py              # OAuth provider ตาม LOGIN_PROVIDERS
    ├── forms/                 # Flask-WTF form, 1 ไฟล์ต่อ 1 feature
    ├── views/                 # Blueprint, 1 ไฟล์ต่อ 1 feature (register อัตโนมัติ)
    ├── utils/
    │   ├── acl.py             # login_manager, @roles_required
    │   ├── error_handling.py  # หน้า 401/403/404/500
    │   └── template_filters.py
    ├── templates/
    │   ├── base/              # layout หลัก, sidebar, footer, error, html_renderer (macro)
    │   ├── components/        # macro ใช้ซ้ำ: pagination, toast
    │   └── <feature>/         # template ของแต่ละ feature
    └── static/                # npm project: Tailwind/DaisyUI, HTMX, jQuery, Phosphor
tests/                         # pytest + mongomock
scripts/                       # run-web, run-worker, npm, init-admin.py
```

## ลำดับการ init ใน `create_app()`

`app_name/web/__init__.py` เรียกตามลำดับนี้:

```
load_config → csrf → views (blueprints + template filters) → cache → db → acl → rq → oauth → error handlers
```

ถ้าจะเพิ่ม extension ใหม่ ให้สร้างไฟล์ใน `web/` ที่มี `init_<name>(app)` แล้วเรียกจาก `create_app()` อย่า init extension ตอน import module

## เพิ่ม feature ใหม่ต้องแตะไฟล์ไหนบ้าง

| ลำดับ | ไฟล์ | หมายเหตุ |
|---|---|---|
| 1 | `models/<plural>.py` + `models/__init__.py` | ต้อง export ใน `__init__` ด้วย |
| 2 | `web/forms/<plural>.py` + `web/forms/__init__.py` | |
| 3 | `web/views/<plural>.py` | register อัตโนมัติ ไม่ต้องแก้ไฟล์อื่น |
| 4 | `web/templates/<plural>/*.html` | |
| 5 | `web/templates/base/sidebar.html` | เพิ่มเมนู (ถ้ามี) |
| 6 | `tests/test_<plural>.py` | |

ตัวอย่างโค้ดครบทุกไฟล์อยู่ใน [09-feature-scaffold.md](09-feature-scaffold.md)
