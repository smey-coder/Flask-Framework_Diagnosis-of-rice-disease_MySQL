from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
)
import logging
from flask_login import login_required

from app.forms.permission_forms import PermissionCreateForm, PermissionEditForm, PermissionConfirmDeleteForm
from app.services.permission_service import PermissionService
from flask_login import current_user

logger = logging.getLogger("app")
permission_bp = Blueprint("tbl_permissions", __name__, url_prefix="/permissions")

@permission_bp.route("/")
@login_required
def index():
    permissions = PermissionService.get_permission_all()
    return render_template("permissions/index.html", permissions=permissions,  user=current_user)

@permission_bp.route("/<int:permission_id>")
@login_required
def detail(permission_id: int):
    permission = PermissionService.get_permission_by_id(permission_id)
    if permission is None:
        abort(404)
    return render_template("permissions/detail.html", permission=permission)

@permission_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = PermissionCreateForm()
    if form.validate_on_submit():
        data = {
            "code": form.code.data,
            "name": form.name.data,
            "module": form.module.data,
            "description": form.description.data,
        }
        permission = PermissionService.create_permission(data)
        flash(f"Permission '{permission.name}' was created successfully.", "success")
        return redirect(url_for("tbl_permissions.index"))
    
    return render_template("permissions/create.html", form=form)
    #     try:
    #         permission = PermissionService.create_permission(data)
    #         flash(f"Permission '{permission.name}' created successfully.", "success")
    #         return redirect(url_for("tbl_permissions.index"))
    #     except Exception as exc:
    #         logger.exception("Failed to create permission: %s", exc)
    #         flash("Failed to create permission.", "danger")
    # elif request.method == "POST":
    #     logger.warning("Permission creation form validation failed: %s", form.errors)
    #     flash("There were errors creating the permission. Please review the form.", "warning")

    # return render_template("permissions/create.html", form=form)

@permission_bp.route("/<int:permission_id>/edit", methods=["GET", "POST"])
@login_required
def edit(permission_id: int):
    permission = PermissionService.get_permission_by_id(permission_id)
    if permission is None:
        abort(404)
    
    form = PermissionEditForm(original_permission=permission, obj=permission)
    
    if form.validate_on_submit():
        data = {
            "code": form.code.data,
            "name": form.name.data,
            "module": form.module.data,
            "description": form.description.data,
        }
        PermissionService.update_permission(permission, data)
        flash(f"Permission '{permission.name}' was updated successfully.", "success")
        return redirect(url_for("tbl_permissions.detail", permission_id=permission.id))

    return render_template("permissions/edit.html", form=form, permission=permission)
    #     try:
    #         PermissionService.update_permission(permission, data)
    #         flash(f"Permission '{permission.name}' updated successfully.", "success")
    #         return redirect(url_for("tbl_permissions.detail", permission_id=permission.id))
    #     except Exception as exc:
    #         flash("Failed to update permission.", "danger")
    #         return render_template("permissions/edit.html", form=form, permission=permission)
    # else:
    #     if request.method == "POST":
    #         import logging
    #         logging.getLogger("app").warning("Permission edit form validation failed for %s: %s", permission_id, form.errors)
    #         flash("There were errors updating the permission. Please review the form.", "warning")
    
    # return render_template("permissions/edit.html", form=form, permission=permission)

@permission_bp.route("/<int:permission_id>/delete", methods=["GET"])
@login_required
def delete_confirm(permission_id: int):
    permission = PermissionService.get_permission_by_id(permission_id)
    if permission is None:
        abort(404)
    
    form = PermissionConfirmDeleteForm()
    return render_template("permissions/delete_confirm.html", permission=permission, form=form)

@permission_bp.route("/<int:permission_id>/delete", methods=["POST"])
@login_required
def delete(permission_id: int):
    permission = PermissionService.get_permission_by_id(permission_id)
    if permission is None:
        abort(404)
    
    try:
        PermissionService.delete(permission)
        flash("Permission deleted successfully.", "success")
    except Exception as exc:
        flash("Failed to delete permission.", "danger")
    
    return redirect(url_for("tbl_permissions.index"))
