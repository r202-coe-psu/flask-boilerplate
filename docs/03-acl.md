# 03 · Access Control (ACL)

## กฎหลัก

> **ทุก route ต้องกำหนดสิทธิ์ผ่าน decorator เท่านั้น**
> ใช้ `@login_required` หรือ `@roles_required([...])` ห้ามเขียน if เช็กสิทธิ์ในตัว view เพื่อกันการเข้าถึงหน้า

| Decorator | Import จาก | ใช้เมื่อ |
|---|---|---|
| `@login_required` | `flask_login` | ผู้ใช้ทุกคนที่ login แล้วเข้าได้ |
| `@roles_required(["admin"])` | `app_name.web.utils.acl` | ต้องมี role ที่กำหนด **อย่างน้อย 1 ตัว** |
| *(ไม่มี decorator)* + comment `# public:` | — | หน้าสาธารณะที่ตั้งใจเปิดให้ทุกคน |

```python
from flask_login import login_required

from app_name.web.utils.acl import roles_required
```

ข้อควรระวังเรื่องชื่อ:
- ชื่อจริงคือ **`roles_required`** (มี s) ไม่ใช่ `role_required`
- argument ต้องเป็น **list** เสมอ: `@roles_required(["admin"])` ไม่ใช่ `@roles_required("admin")` ถ้าส่ง string มา ตัว `in` จะเช็กทีละตัวอักษร
- `roles_required` ตรวจการ login ให้ในตัวแล้ว ไม่ต้องใส่ `@login_required` ซ้อนอีกชั้น

## ลำดับ decorator

`@module.route(...)` ต้องอยู่**บนสุด** แล้วตามด้วย ACL decorator

```python
# ✅ ถูก: route register function ที่ถูกห่อด้วย ACL แล้ว
@module.route("/<project_id>/delete", methods=["POST"])
@roles_required(["admin"])
def delete(project_id): ...


# ❌ ผิด: route register function เปล่าไปก่อน ACL จึงไม่ถูกเรียกเลย
@roles_required(["admin"])
@module.route("/<project_id>/delete", methods=["POST"])
def delete(project_id): ...
```

ถ้ามีหลาย `@module.route` (เช่น `create_or_edit`) ให้วาง route ทั้งหมดไว้บนสุด แล้ว ACL ตามมาเป็นบรรทัดสุดท้ายก่อน `def`

## หน้า Public

route ที่ตั้งใจเปิดให้คนที่ไม่ได้ login เข้าได้ **ต้องเขียน comment บอกเหตุผล**ไว้เหนือ decorator ให้ reviewer รู้ว่าตั้งใจ ไม่ใช่ลืมใส่

```python
# public: landing page
@module.route("/")
def index(): ...


# public: health check for load balancer / docker
@module.route("/healthz")
def healthz(): ...
```

route ใน boilerplate ที่เป็น public อยู่แล้ว: `index.index`, `accounts.login`, `accounts.login_oauth`, `accounts.authorized_oauth`, `api.healthz`

## เมื่อไหร่ "เช็กสิทธิ์ใน view" ได้

decorator ตอบได้แค่ว่า "คนนี้เข้า **หน้านี้** ได้ไหม" ส่วนคำถามว่า "คนนี้เข้าถึง **record นี้** ได้ไหม" (data scope / ownership) ให้เช็กใน view ได้ **โดยต้องมี decorator อยู่ก่อนแล้ว**

```python
@module.route("/<project_id>/edit", methods=["GET", "POST"])
@login_required                                   # 1) ต้อง login ก่อน (decorator)
def create_or_edit(project_id):
    project = models.Project.objects.get(id=project_id)
    if project.creator.id != current_user.id and not current_user.is_admin():
        abort(403)                                # 2) data scope: ต้องเป็นเจ้าของ
    ...
```

หรือใช้วิธี filter queryset ตามสิทธิ์ เพื่อไม่ให้มองเห็นข้อมูลของคนอื่นตั้งแต่แรก

```python
projects = models.Project.objects(status="active")
if not current_user.is_admin():
    projects = projects.filter(creator=current_user.id)
```

```python
# ❌ ห้าม: ใช้ if แทน decorator เพื่อกันการเข้าหน้า
@module.route("/settings")
def settings():
    if "admin" not in current_user.roles:
        abort(403)
```

## Template ไม่ใช่ security

การซ่อนเมนูหรือปุ่มใน template เช่น `{% if current_user.is_admin() %}` ใน `base/sidebar.html` **เป็นแค่ UX** ผู้ใช้ยังพิมพ์ URL หรือยิง POST ตรงเข้ามาได้ ดังนั้นทุก endpoint ที่ปุ่มนั้นเรียก ต้องมี decorator ของตัวเองเสมอ

กฎเดียวกันใช้กับ:
- endpoint ที่ HTMX เรียก (`hx-get`, `hx-post`)
- endpoint ที่คืน JSON
- endpoint ที่ถูกเรียกจาก `fetch()` ใน JavaScript

## พฤติกรรมเมื่อไม่ผ่าน

| สถานการณ์ | ผลลัพธ์ |
|---|---|
| ยังไม่ login | redirect ไป `accounts.login?next=<url เดิม>` (กำหนดไว้ที่ `login_manager.login_view`) |
| login แล้วแต่ role ไม่ตรง | `403` render ด้วย `base/error.html` |
| บัญชี `status="inactive"` | login ไม่ได้ (`User.is_active` คืน `False`) |

## Role

Role ทั้งหมดประกาศไว้ที่ `USER_ROLES` ใน `app_name/models/users.py`

```python
USER_ROLES = [
    ("user", "ผู้ใช้งานทั่วไป"),
    ("admin", "ผู้ดูแลระบบ"),
]
```

ขั้นตอนเพิ่ม role ใหม่:
1. เพิ่ม tuple `(value, label ภาษาไทย)` ใน `USER_ROLES` โดยให้ value เป็นภาษาอังกฤษ snake_case เช่น `("camp_staff", "เจ้าหน้าที่ศูนย์")`
2. ถ้าต้องใช้ใน template บ่อย ให้เพิ่ม helper method ใน `User` เช่น `def is_camp_staff(self): return self.has_role("camp_staff")`
3. ใช้ใน view ผ่าน `@roles_required(["admin", "camp_staff"])`

ห้ามสร้าง role ใหม่ด้วยการพิมพ์ string ลอย ๆ ใน decorator โดยไม่เพิ่มใน `USER_ROLES`

## Checklist สำหรับ reviewer

- [ ] ทุก `@module.route` มี `@login_required` / `@roles_required([...])` อยู่ถัดลงมา หรือมี comment `# public:`
- [ ] ลำดับ decorator ถูก (route อยู่บนสุด)
- [ ] `roles_required` รับเป็น list
- [ ] ไม่มีการเช็ก role ด้วย `if` แทน decorator
- [ ] ถ้าข้อมูลเป็นของเฉพาะคน มีการเช็ก data scope หรือ filter queryset
- [ ] ปุ่มที่ซ่อนใน template มี endpoint ที่ป้องกันด้วย decorator จริง
- [ ] มี test ว่า "ไม่ login → redirect" และ "role ไม่พอ → 403" ดู [07-testing.md](07-testing.md)
