# 06 · Background Jobs, Cache และ Config

## Background jobs (RQ)

งานที่ใช้เวลานานกว่าประมาณ 2–3 วินาที (import/export ไฟล์, ส่งอีเมลจำนวนมาก, เรียก API ภายนอกที่ช้า) **ต้องส่งไปทำใน worker** ห้ามทำใน request

### เขียน task

ทุก task อยู่ใน `app_name/worker/tasks.py` (ถ้ามีเยอะให้แยกเป็น `worker/tasks/<feature>.py`)

```python
def export_projects(user_id: str, file_id: str):
    user = models.User.objects.with_id(user_id)
    ...
```

กฎ:
- **argument ส่งเป็นค่า primitive** (`str`, `int`, `dict`) ส่วน document ให้ส่ง `str(doc.id)` แล้วไปโหลดใหม่ใน task ห้ามส่ง Document object เพราะ RQ ต้อง pickle ข้อมูล และข้อมูลอาจเก่าไปแล้วตอนที่ job เริ่มทำงาน
- task ทำงาน**นอก Flask app context**: ใช้ `request`, `current_user`, `url_for`, `flash` ไม่ได้ และ worker connect DB ให้แล้วใน `worker/server.py`
- task ควรรันซ้ำได้โดยไม่พัง (idempotent) เพราะ job อาจถูก retry
- สถานะงานที่ผู้ใช้ต้องติดตาม ให้เก็บใน document ของตัวเอง (เช่น `ExportFile.status = pending/done/failed`) ไม่พึ่ง RQ job อย่างเดียว เพราะ job result ใน Redis มีวันหมดอายุ

### Enqueue จาก view

```python
from app_name.web.redis_rq import redis_queue
from app_name.worker import tasks

job = redis_queue.enqueue(tasks.export_projects, str(current_user.id), str(export_file.id))
flash("กำลังสร้างไฟล์ ระบบจะแจ้งเมื่อเสร็จ", "warning")
```

## Cache (Flask-Caching + Redis)

ใช้ `cache` จาก `app_name/web/caches.py` ตามแบบ `dashboard.get_summary`

```python
from app_name.web.caches import cache


@cache.memoize(timeout=60)
def get_summary():
    ...
```

กฎ:
- cache ที่ระดับ **function ที่คืนข้อมูล** ไม่ cache ทั้ง view ที่มีข้อมูลเฉพาะผู้ใช้ (ไม่อย่างนั้นข้อมูลจะหลุดไปให้คนอื่นเห็น)
- ระบุ `timeout` ทุกครั้ง
- ถ้าข้อมูลเปลี่ยนแล้วต้องเห็นผลทันที ให้ invalidate หลัง save: `cache.delete_memoized(get_summary)`
- argument ของ function ที่ memoize ต้อง hash ได้และคงที่ ให้ส่งเป็น id ไม่ใช่ document
- ใน test ใช้ `CACHE_TYPE = "NullCache"` (ตั้งไว้แล้วใน `tests/conftest.py`)

## Config

### ลำดับการโหลด

`web/config.py:load_config()` โหลดตามลำดับนี้ ตัวหลังทับตัวก่อน:

1. `app_name/default_settings.py`: ค่า default
2. ไฟล์ `.env` ที่ root ของโปรเจกต์ (เปลี่ยน path ได้ด้วย env var `APP_SETTINGS`)
3. Environment variables ของ process **เฉพาะ key ที่มีอยู่แล้วจากข้อ 1 หรือ 2**

ทั้ง web และ worker ใช้ function เดียวกัน ค่าจึงตรงกันเสมอ

### เพิ่ม config ใหม่

1. เพิ่มค่า default ใน `default_settings.py` (ถ้าเป็น secret ให้ default เป็นค่าว่าง)
2. เพิ่มตัวอย่างใน `.env.example` พร้อม comment อธิบาย
3. อ่านค่าใน view ด้วย `current_app.config["KEY"]` ส่วนใน template ใช้ `config.KEY`
4. ชื่อ key เป็น UPPER_SNAKE_CASE และขึ้นต้นด้วยชื่อระบบที่เกี่ยวข้อง เช่น `SMTP_HOST`, `LINE_NOTIFY_TOKEN`

`.env` แปลงชนิดให้อัตโนมัติ: `true/false` → bool, ตัวเลขล้วน → int, `LOGIN_PROVIDERS` → list (คั่นด้วย comma), `*_CLIENT_KWARGS` → dict

### Secret

- **ห้าม commit `.env`** (อยู่ใน `.gitignore` แล้ว) และห้าม hardcode password, token หรือ API key ในโค้ดหรือ script
- production ต้องเปลี่ยน `SECRET_KEY` เป็นค่าสุ่มยาว ๆ เช่น `python -c "import secrets; print(secrets.token_urlsafe(48))"`
- ห้าม log หรือ `print` ค่า config ทั้งก้อน เพราะมี secret ปนอยู่
