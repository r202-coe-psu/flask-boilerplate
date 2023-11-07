from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    validators,
)


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        [
            validators.DataRequired("Username is required."),
            validators.Length(min=4, max=5),
        ],
    )
    password = PasswordField(
        "Password", [validators.DataRequired("Password is required.")]
    )
    submit = SubmitField("Login")
