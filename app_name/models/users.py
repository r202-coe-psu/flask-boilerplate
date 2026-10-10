import datetime

import mongoengine as me
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

USER_ROLES = [
    ("user", "ผู้ใช้งานทั่วไป"),
    ("admin", "ผู้ดูแลระบบ"),
]

STATUS_CHOICES = [
    ("active", "ใช้งาน"),
    ("inactive", "ไม่ใช้งาน"),
]


class User(me.Document, UserMixin):
    meta = {"collection": "users", "indexes": ["username", "email"]}

    display_name = me.StringField(default="")
    first_name = me.StringField(max_length=128)
    last_name = me.StringField(max_length=128)
    username = me.StringField(required=True, min_length=3, max_length=64)
    password = me.StringField(required=True, default="")
    email = me.StringField(max_length=128)

    status = me.StringField(
        required=True,
        default="active",
        choices=[status[0] for status in STATUS_CHOICES],
    )
    roles = me.ListField(me.StringField(choices=[role[0] for role in USER_ROLES]))

    # Raw user info from each OAuth2 provider, keyed by provider name
    resources = me.DictField()

    is_setup_password = me.BooleanField(default=False)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    creator = me.ReferenceField("User", dbref=True)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updater = me.ReferenceField("User", dbref=True)
    last_login_date = me.DateTimeField()

    @property
    def is_active(self):
        return self.status == "active"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if not self.password:
            return False
        return check_password_hash(self.password, password)

    def get_fullname(self):
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    def display_status(self):
        return dict(STATUS_CHOICES).get(self.status, self.status)

    def get_display_roles(self):
        role_dict = dict(USER_ROLES)
        return [role_dict.get(role, role) for role in self.roles]

    def has_role(self, role):
        return role in self.roles

    def is_admin(self):
        return self.has_role("admin")
