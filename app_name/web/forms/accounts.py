from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators


class LoginForm(FlaskForm):
    username = StringField(
        "ชื่อผู้ใช้",
        validators=[validators.InputRequired(), validators.Length(min=3, max=64)],
    )
    password = PasswordField("รหัสผ่าน", validators=[validators.InputRequired()])


class SetupPasswordForm(FlaskForm):
    password = PasswordField(
        "รหัสผ่าน",
        validators=[validators.InputRequired(), validators.Length(min=8)],
    )
    confirm_password = PasswordField(
        "ยืนยันรหัสผ่าน",
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="รหัสผ่านทั้งสองช่องไม่ตรงกัน"),
        ],
    )
