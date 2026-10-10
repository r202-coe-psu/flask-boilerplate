# 04 · Models (MongoEngine)

## ไฟล์และการตั้งชื่อ

- 1 domain ต่อ 1 ไฟล์: `app_name/models/<plural>.py` เช่น `models/projects.py`
- ชื่อ class เป็น **เอกพจน์** PascalCase เช่น `Project`
- ชื่อ collection เป็นพหูพจน์ snake_case และ**ต้องระบุใน `meta` เสมอ** (ไม่ปล่อยให้ MongoEngine ตั้งเอง จะได้เปลี่ยนชื่อ class ทีหลังได้โดยข้อมูลไม่หาย)
- ทุก model ต้อง import และใส่ใน `__all__` ของ `models/__init__.py` แล้วโค้ดส่วนอื่นเรียกผ่าน `models.Project` เสมอ

```python
# models/__init__.py
from .users import User, USER_ROLES
from .oauth2 import OAuth2Token
from .projects import Project, PROJECT_STATUS_CHOICES

__all__ = [
    "User",
    "USER_ROLES",
    "OAuth2Token",
    "Project",
    "PROJECT_STATUS_CHOICES",
]
```

## Field มาตรฐาน

ทุก model ที่ผู้ใช้สร้างหรือแก้ได้ ต้องมี field กลุ่มนี้ (ตามแบบ `User`):

```python
status = me.StringField(
    required=True,
    default="active",
    choices=[status[0] for status in PROJECT_STATUS_CHOICES],
)

created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
creator = me.ReferenceField("User", dbref=True)
updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
updater = me.ReferenceField("User", dbref=True)
```

| Field | ใช้ทำอะไร | ใครเป็นคน set |
|---|---|---|
| `status` | soft delete (`active` / `inactive`) และสถานะอื่นตาม domain | view |
| `created_date` | วันที่สร้าง | default |
| `creator` | คนสร้าง | view ตอน create |
| `updated_date` | แก้ไขล่าสุด | view ทุกครั้งที่ save (**set เอง** ไม่ใช้ `auto_now`) |
| `updater` | คนแก้ล่าสุด | view ทุกครั้งที่ save |

## ค่าของ `status`: ใช้ `active` คู่กับ `inactive` เท่านั้น

สถานะ "เปิด/ปิดการใช้งาน" มีค่าที่อนุญาตแค่ 2 คำ และเขียนแบบนี้ทุก model ทุกโปรเจกต์:

| ค่า | ความหมาย | label |
|---|---|---|
| `active` | ใช้งานอยู่ (ค่า default) | `ใช้งาน` |
| `inactive` | ปิดการใช้งาน / ถูกลบแบบ soft delete | `ปิดการใช้งาน` |

**ห้ามใช้** `disactive`, `deactive`, `deactivate`, `deactivated` หรือคำอื่นที่หมายถึงสถานะเดียวกัน ทั้งในค่า field, choices, query, test และ template

```python
# ✅ ถูก
project.status = "inactive"
models.Project.objects(status="active")

# ❌ ผิด
project.status = "disactive"
project.status = "deactive"
if user.status == "deactivate": ...
```

เหตุผล: ถ้าสะกดหลายแบบ query เช่น `objects(status="inactive")` จะหาข้อมูลไม่ครบโดยไม่มี error เตือน และถ้าค่าใน DB ปนกันหลายคำแล้วจะต้องเขียน migration ไล่แก้ทีหลัง

ถ้า domain ต้องมีสถานะอื่นเพิ่ม (เช่น `pending`, `approved`, `back_home`) ให้เพิ่มเป็นค่าใหม่ใน `<MODEL>_STATUS_CHOICES` ได้ แต่ความหมาย "เปิด/ปิดการใช้งาน" ต้องใช้ `active` / `inactive` เสมอ

## Choices

ประกาศเป็นค่าคงที่ระดับ module ในรูป `(value, label ภาษาไทย)` แล้วตั้งชื่อเป็น `<FIELD>_CHOICES` หรือ `<MODEL>_<FIELD>_CHOICES` ถ้ามีโอกาสชนกับชื่ออื่น

```python
PROJECT_STATUS_CHOICES = [
    ("active", "ใช้งาน"),
    ("inactive", "ปิดการใช้งาน"),
]
```

- ใน field ให้ใช้ `choices=[c[0] for c in ...]` เพื่อ validate เฉพาะ value
- เพิ่ม method `display_<field>()` ใน model สำหรับแสดง label ใน template ห้ามเขียน mapping ซ้ำใน template

```python
def display_status(self):
    return dict(PROJECT_STATUS_CHOICES).get(self.status, self.status)
```

## Reference

- อ้างอิง model อื่นด้วย **string** เพื่อเลี่ยง circular import: `me.ReferenceField("User", dbref=True)`
- field ที่ใช้ filter หรือ sort บ่อยต้องอยู่ใน `meta["indexes"]`

## Query

- **ระวัง N+1**: การเข้าถึง `project.creator.username` ใน loop จะ query ทีละ record ถ้า list ยาวให้ใช้ `.select_related()` หรือ `aggregate()`
- ห้ามดึงทั้ง collection มา filter ใน Python ให้ filter ใน query
- นับจำนวนใช้ `.count()` และหาผลรวมใช้ `.sum("field")` ไม่ใช้ `len(list(...))`
- ใช้ `.only(...)` เมื่อต้องการแค่บาง field จาก collection ใหญ่

## Method ใน model

ใส่ได้เฉพาะ logic ที่เกี่ยวกับ document ตัวเองล้วน ๆ เช่น `get_fullname()`, `display_status()`, `has_role()` ห้ามใส่สิ่งที่ต้องใช้ `request`, `current_user` หรือ Flask context ใน model เพราะ worker และ script ก็ import model ตัวเดียวกัน

## เชื่อมต่อ DB นอก Flask

Worker และ script ไม่มี Flask app ให้ connect ผ่าน `models.init_mongoengine(settings)` ตามแบบใน `worker/server.py` และ `scripts/init-admin.py`

```python
from app_name import models
from app_name.web.config import get_settings

models.init_mongoengine(get_settings())
```

## การเปลี่ยน schema ของข้อมูลเดิม

MongoDB ไม่มี migration อัตโนมัติ ถ้าเพิ่ม field ที่ `required=True` หรือเปลี่ยนชื่อ field:
1. ใส่ `default=` ให้ field ใหม่เสมอ เพื่อให้ document เก่ายังโหลดได้
2. ถ้าต้องแปลงข้อมูลเก่า ให้เขียน script ใน `scripts/migrate-<yyyymmdd>-<เรื่อง>.py` ที่รันซ้ำได้โดยไม่พัง (idempotent) แล้วระบุใน PR ว่าต้องรัน
