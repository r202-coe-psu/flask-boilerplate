# 07 · Testing และ Lint

## คำสั่ง

```bash
poetry run pytest              # รัน test ทั้งหมด
poetry run pytest tests/test_projects.py -k delete   # เฉพาะบาง test
poetry run ruff check .        # lint
poetry run ruff format .       # format โค้ด
```

**ต้องรันทั้ง `pytest` และ `ruff check` ให้ผ่านก่อน push ทุกครั้ง** ตอนนี้ repo ยังไม่มี CI ที่รันให้อัตโนมัติ

## Fixture ที่มีให้ (`tests/conftest.py`)

| Fixture | ได้อะไร |
|---|---|
| `app` | Flask app ที่ใช้ **mongomock** (ไม่ต้องมี MongoDB จริง), ปิด CSRF, `NullCache` และ DB จะถูกล้างทุก collection หลังจบแต่ละ test |
| `client` | `app.test_client()` ที่ยังไม่ login |
| `admin` | `User` ที่มี role `admin` (รหัสผ่าน `password1234`) |
| `admin_client` | `client` ที่ login เป็น `admin` แล้ว |

ถ้าต้องการผู้ใช้ role อื่น ให้สร้าง fixture ในไฟล์ test ของ feature นั้น (ดูตัวอย่าง `user_client` ใน [09-feature-scaffold.md](09-feature-scaffold.md)) ถ้าหลายไฟล์ใช้ร่วมกันค่อยย้ายไป `conftest.py`

## Test ขั้นต่ำที่ทุก feature ต้องมี

ไฟล์ `tests/test_<feature>.py`:

| # | Test | ตรวจอะไร |
|---|---|---|
| 1 | ไม่ login → redirect | `GET /<feature>` ได้ `302` และ `Location` มี `/login` |
| 2 | role ไม่พอ → 403 | POST create/edit/delete ด้วย user ที่ไม่มีสิทธิ์ได้ `403` และข้อมูลใน DB ไม่เปลี่ยน |
| 3 | list / view | ได้ `200` |
| 4 | create | ได้ `302` และ document ถูกสร้างพร้อม `creator` |
| 5 | edit | ได้ `302` และค่าใน DB เปลี่ยน (ใช้ `doc.reload()`) |
| 6 | delete | `status` เป็น `inactive` (soft delete) |

ข้อ 1 กับ 2 สำคัญที่สุด เพราะเป็นตัวยืนยันว่า ACL ตาม [03-acl.md](03-acl.md) ถูกใส่ครบ

## แนวทางเขียน test

- 1 test ตรวจ 1 พฤติกรรม และตั้งชื่อเป็นประโยค เช่น `test_user_cannot_create`
- ตรวจผลที่ **DB** ด้วย ไม่ใช่แค่ status code
- ไม่ต้องส่ง `csrf_token` ใน test เพราะ fixture ปิด CSRF ไว้แล้ว
- อย่าให้ test พึ่งลำดับการรันหรือข้อมูลจาก test อื่น ให้สร้างข้อมูลผ่าน fixture
- test ที่เกี่ยวกับ OAuth หรือ API ภายนอก ให้ mock ด้วย `monkeypatch` ห้ามยิงออก network จริง

## Lint / Format

- ใช้ **ruff** ตัวเดียว ทั้ง lint และ format (config อยู่ใน `pyproject.toml`)
- ห้ามปิด rule ด้วย `# noqa` ถ้าไม่จำเป็น ถ้าต้องใช้ให้ระบุ rule เช่น `# noqa: E402` พร้อมเหตุผล
