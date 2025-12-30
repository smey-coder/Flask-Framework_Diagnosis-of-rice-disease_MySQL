from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import login_required

from app.forms.user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from app.services.user_service import UserService
from app.models.role import RoleTable


user_bp = Blueprint("tbl_users", __name__, url_prefix="/users")

@user_bp.route("/")
@login_required
def index():
    users = UserService.get_user_all()
    return render_template("users/index.html", users=users)

@user_bp.route("/<int:user_id>")
@login_required
def detail(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
    return render_template("users/detail.html", user=user)

@user_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = UserCreateForm()
    
    roles = RoleTable.query.all()
    form.role_id.choices = [(role.id, role.name) for role in roles]
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data
        role_id = form.role_id.data or None
        
        user = UserService.create_user(data, password, role_id)
        flash(f"User '{user.username}' was created successfully.", "success")
        return redirect(url_for("tbl_users.index"))
    
    return render_template("users/create.html", form=form)

@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
        
    form = UserEditForm(original_user=user, obj=user)
    
    roles = RoleTable.query.all()
    form.role_id.choices = [(role.id, role.name) for role in roles]
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data or None
        role_id = form.role_id.data or None
        
        UserService.update_user(user, data, password, role_id)
        flash(f"User '{user.username}' was updated successfully.", "success")
        return redirect(url_for("tbl_users.detail", user_id=user.id))

    return render_template("users/edit.html", form=form, user=user)

@user_bp.route("/<int:user_id>/delete", methods=["GET"])
@login_required
def delete_confirm(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
        
    form = UserConfirmDeleteForm()
    return render_template("users/delete_confirm.html", user=user,form=form)

@user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
def delete(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
        
    UserService.delete_user(user)
    flash("User was deleted successfully.", "success")
    return redirect(url_for("tbl_users.index"))

    