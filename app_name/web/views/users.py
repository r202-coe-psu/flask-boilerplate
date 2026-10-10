import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_mongoengine import Pagination
from mongoengine.queryset.visitor import Q

from app_name import models
from app_name.web import forms
from app_name.web.utils.acl import roles_required

module = Blueprint("users", __name__, url_prefix="/users")

PER_PAGE = 20


@module.route("")
@roles_required(["admin"])
def index():
    page = request.args.get("page", 1, type=int)
    form = forms.users.SearchUserForm(request.args)

    users = models.User.objects().order_by("-created_date")
    search = (form.search.data or "").strip()
    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    try:
        pagination = Pagination(users, page, per_page=PER_PAGE)
    except Exception:
        pagination = Pagination(users, 1, per_page=PER_PAGE)

    return render_template(
        "users/index.html",
        users_pagination=pagination,
        form=form,
        search=search,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"user_id": None})
@module.route("/<user_id>/edit", methods=["GET", "POST"])
@roles_required(["admin"])
def create_or_edit(user_id):
    user = models.User()
    form = forms.users.CreateUserForm()
    if user_id:
        user = models.User.objects.get(id=user_id)
        form = forms.users.EditUserForm(obj=user)

    if not form.validate_on_submit():
        return render_template("users/create_or_edit.html", form=form, user=user)

    duplicated = models.User.objects(username=form.username.data, id__ne=user.id)
    if duplicated.first():
        flash("ชื่อบัญชีนี้มีผู้ใช้งานแล้ว", "error")
        return render_template("users/create_or_edit.html", form=form, user=user)

    # Only copy model fields; password fields are hashed separately below
    for name in ["username", "first_name", "last_name", "email", "roles"]:
        setattr(user, name, form[name].data)

    if not user_id:
        user.set_password(form.password.data)
        user.creator = current_user._get_current_object()
    elif form.reset_password.data:
        user.set_password(form.reset_password.data)

    user.updater = current_user._get_current_object()
    user.updated_date = datetime.datetime.now()
    user.save()

    flash("บันทึกข้อมูลผู้ใช้งานเรียบร้อยแล้ว", "success")
    return redirect(url_for("users.index"))


@module.route("/<user_id>/delete", methods=["POST"])
@roles_required(["admin"])
def delete(user_id):
    user = models.User.objects.get(id=user_id)
    user.status = "inactive"
    user.updater = current_user._get_current_object()
    user.updated_date = datetime.datetime.now()
    user.save()

    flash("ปิดการใช้งานบัญชีเรียบร้อยแล้ว", "success")
    return redirect(url_for("users.index"))
