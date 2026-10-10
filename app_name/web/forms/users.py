from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    PasswordField,
    SelectMultipleField,
    StringField,
    validators,
)

from app_name.models.users import USER_ROLES


class BaseUserForm(FlaskForm):
    username = StringField(
        "ชื่อบัญชี (Username)",
        [validators.InputRequired(), validators.Length(min=3, max=64)],
    )
    first_name = StringField("ชื่อจริง", [validators.Length(max=128)])
    last_name = StringField("นามสกุล", [validators.Length(max=128)])
    email = EmailField(
        "อีเมล", [validators.Optional(), validators.Email(), validators.Length(max=128)]
    )


class CreateUserForm(BaseUserForm):
    password = PasswordField(
        "รหัสผ่าน",
        [validators.DataRequired(), validators.Length(min=8)],
        description="รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร",
    )
    roles = SelectMultipleField(
        "บทบาทผู้ใช้งาน",
        choices=USER_ROLES,
        validators=[validators.DataRequired()],
    )


class EditUserForm(BaseUserForm):
    roles = SelectMultipleField(
        "บทบาทผู้ใช้งาน",
        choices=USER_ROLES,
        validators=[validators.DataRequired()],
    )
    reset_password = PasswordField(
        "รีเซ็ตรหัสผ่าน",
        [validators.Optional(), validators.Length(min=8)],
        description="ระบุรหัสผ่านใหม่หากต้องการรีเซ็ตรหัสผ่าน",
    )


class SearchUserForm(FlaskForm):
    class Meta:
        csrf = False

    search = StringField(
        "ค้นหาผู้ใช้งาน",
        [validators.Optional(), validators.Length(max=64)],
    )
