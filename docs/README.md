# Developer Guideline

เอกสารชุดนี้คือข้อตกลงในการเขียนโค้ดสำหรับทุกโปรเจกต์ที่สร้างจาก boilerplate นี้
เป้าหมายคือให้ทุกคนในทีม (และ AI coding agent) เขียนโค้ดออกมาหน้าตาเดียวกัน อ่านง่าย review ง่าย และปลอดภัยเป็นค่าเริ่มต้น

> ตัวอย่างในเอกสารอ้างชื่อ package `app_name` ถ้าโปรเจกต์ของคุณ rename แล้ว ให้แทนด้วยชื่อ package จริง

## อ่านอะไรก่อน

ถ้าเพิ่งเข้ามาในโปรเจกต์ ให้อ่านตามลำดับนี้:

1. [โครงสร้างโปรเจกต์](01-project-structure.md): ไฟล์ไหนอยู่ตรงไหน ทำหน้าที่อะไร
2. [Route และ CRUD convention](02-routes-crud.md): การตั้งชื่อ URL, function, blueprint, template ⭐
3. [Access Control (ACL)](03-acl.md): กฎการกำหนดสิทธิ์ผ่าน decorator ⭐
4. [ตัวอย่าง Feature ครบชุด](09-feature-scaffold.md): copy ไปเริ่มงานได้เลย

ที่เหลือเปิดอ่านเมื่อต้องใช้:

| เอกสาร | เรื่อง |
|---|---|
| [04-models.md](04-models.md) | MongoEngine model, field มาตรฐาน, index, soft delete |
| [05-forms-templates.md](05-forms-templates.md) | WTForms, Jinja layout, macro, flash, HTMX, CSRF |
| [06-jobs-cache-config.md](06-jobs-cache-config.md) | Background job (RQ), cache, config และ secret |
| [07-testing.md](07-testing.md) | pytest fixture, test ขั้นต่ำที่ต้องมี, lint |
| [08-git-workflow.md](08-git-workflow.md) | Branch, commit message, PR checklist |

## กฎ 5 ข้อที่ห้ามลืม

1. **ทุก route ต้องมี `@login_required` หรือ `@roles_required([...])`** ถ้าเป็นหน้า public ต้องเขียน `# public: <เหตุผล>` กำกับไว้ ดู [03-acl.md](03-acl.md)
2. **ห้ามเปลี่ยนข้อมูลด้วย GET**: create/update/delete ต้องเป็น POST และมี CSRF token
3. **ตั้งชื่อตาม convention** ทั้ง `views/<plural>.py`, `module = Blueprint("<plural>", ...)` และ `index / view / create_or_edit / delete` ดู [02-routes-crud.md](02-routes-crud.md)
4. **ไม่ลบข้อมูลจริง** ให้ใช้ soft delete ด้วยการตั้ง `status = "inactive"`
5. **ทุก feature ต้องมี test** อย่างน้อยครอบคลุม happy path, กรณีไม่ login และกรณี role ไม่พอ
