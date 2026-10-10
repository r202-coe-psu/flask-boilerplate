# 08 · Git Workflow

## Branch

| Branch | ใช้ทำอะไร | แตกจาก | merge เข้า |
|---|---|---|---|
| `main` | โค้ดที่ deploy production | — | — |
| `develop` | รวมงานที่เสร็จแล้ว รอ release | `main` | `main` |
| `feature/<เรื่อง>` | feature ใหม่ | `develop` | `develop` |
| `fix/<เรื่อง>` | แก้ bug ที่ยังไม่ขึ้น production | `develop` | `develop` |
| `hotfix/<เรื่อง>` | แก้ bug ด่วนบน production | `main` | `main` และ `develop` |

ชื่อ branch เป็นภาษาอังกฤษ kebab-case เช่น `feature/project-export`, `fix/login-redirect`

## Commit message

รูปแบบ:

```
<type>: <สรุปสั้น ๆ ว่าทำอะไร>

<รายละเอียดเพิ่มเติม (ถ้ามี): ทำไมต้องเปลี่ยน, ผลกระทบ>
```

| Type | ใช้เมื่อ |
|---|---|
| `feat` | เพิ่มความสามารถใหม่ |
| `fix` | แก้ bug |
| `hotfix` | แก้ bug ด่วนบน production |
| `refactor` | ปรับโครงสร้างโค้ดโดยพฤติกรรมไม่เปลี่ยน |
| `style` | แก้ UI/CSS หรือ format โค้ด |
| `docs` | แก้เอกสาร |
| `test` | เพิ่ม/แก้ test อย่างเดียว |
| `chore` | งานอื่น ๆ เช่น dependency, config, script |

กฎ:
- type เป็น**ตัวพิมพ์เล็ก** ตามด้วย `: ` (มี space)
- บรรทัดแรกไม่เกินประมาณ 72 ตัวอักษร เขียนบอกว่า "ทำอะไร" ไม่ใช่ "แก้ไฟล์ไหน"
- เขียนเป็นภาษาไทยหรืออังกฤษก็ได้ แต่ใน PR เดียวกันให้ใช้ภาษาเดียวกัน
- 1 commit ต่อ 1 เรื่อง ไม่รวม refactor กับ feature ไว้ใน commit เดียว

```
✅ feat: เพิ่มหน้าจัดการโปรเจกต์
✅ fix: redirect หลัง login ไปหน้าเดิมไม่ได้เมื่อมี query string
✅ chore: upgrade flask to 3.1.3
❌ update
❌ Fix bug
❌ แก้ไฟล์ users.py
```

## Pull Request

- เปิด PR เข้า `develop` (ยกเว้น `hotfix/*` ที่เปิดเข้า `main`)
- ชื่อ PR ใช้รูปแบบเดียวกับ commit message
- PR ไม่ควรใหญ่เกินประมาณ 400 บรรทัด (ไม่นับ lock file) ถ้าใหญ่กว่านั้นให้แบ่งเป็นหลาย PR
- ต้องมี reviewer approve อย่างน้อย 1 คนก่อน merge

### PR description

```markdown
## ทำอะไร
<สรุปการเปลี่ยนแปลง>

## ทำไม
<ปัญหาหรือ requirement ที่มา / ลิงก์ issue>

## ทดสอบอย่างไร
<คำสั่ง test, ขั้นตอนทดสอบด้วยมือ>

## ภาพหน้าจอ
<ถ้ามีการเปลี่ยน UI>

## ต้องทำอะไรเพิ่มตอน deploy
<config ใหม่ใน .env, migration script, หรือ "ไม่มี">
```

### Checklist ก่อนขอ review

- [ ] `poetry run pytest` ผ่าน
- [ ] `poetry run ruff check .` ผ่าน
- [ ] route ใหม่ทุกตัวมี ACL decorator ตาม [03-acl.md](03-acl.md)
- [ ] ตั้งชื่อตาม [02-routes-crud.md](02-routes-crud.md)
- [ ] มี test ขั้นต่ำตาม [07-testing.md](07-testing.md)
- [ ] ไม่มี secret, `.env`, `print()` สำหรับ debug หรือโค้ดที่ comment ทิ้งไว้
- [ ] config ใหม่เพิ่มใน `default_settings.py` และ `.env.example` แล้ว
- [ ] ถ้าเปลี่ยน schema มี default หรือ migration script สำหรับข้อมูลเดิม
- [ ] rebuild CSS แล้ว (ถ้าใช้ Tailwind class ใหม่)
