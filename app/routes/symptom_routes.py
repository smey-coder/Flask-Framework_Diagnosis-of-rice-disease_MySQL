import logging
import os
import uuid
from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_required
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from app.forms.symptom_forms import (
    SymptomCreateForm,
    SymptomEditForm,
    SymptomConfirmDeleteForm,
    SymptomSearchForm,
)
from app.services.symptom_service import SymptomService
from app.decorators.access import role_required, permission_required

logger = logging.getLogger("app")

symptom_bp = Blueprint("tbl_symptoms", __name__, url_prefix="/symptoms")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- INDEX / SEARCH ---------- #
@symptom_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_SYMPTOM")
def index():
    try:
        form = SymptomSearchForm(request.args)
        page = request.args.get("page", 1, type=int)

        # Handle search filters
        symptom_name = request.args.get("symptom_name", "").strip()
        symptom_group = request.args.get("symptom_group", "").strip()
        is_active = request.args.get("is_active", None)

        if symptom_name or symptom_group or is_active is not None:
            pagination = SymptomService.search_symptoms(
                symptom_name=symptom_name,
                symptom_group=symptom_group,
                is_active=is_active,
                page=page,
                per_page=10,
            )
        else:
            pagination = SymptomService.get_symptom_all(page=page, per_page=10)

        return render_template(
            "symptom_page/index.html",
            pagination=pagination,
            symptoms=pagination.items,
            form=form,
        )
    except Exception as e:
        logger.error(f"Symptom Load Error: {e}")
        flash("Can't load symptoms list.", "danger")
        return redirect(url_for("admin.dashboard"))


# ---------- DETAIL ---------- #
@symptom_bp.route("/<int:symptom_id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("DETAIL_SYMPTOM")
def detail(symptom_id: int):
    try:
        symptom = SymptomService.get_symptom_by_id(symptom_id)
        if symptom is None:
            abort(404)
        return render_template("symptom_page/detail.html", symptom=symptom)
    except Exception as e:
        logger.error(f"Symptom Detail Error: {e}")
        flash("An error occurred while loading symptom details.", "danger")
        return redirect(url_for("tbl_symptoms.index"))


# ---------- CREATE ---------- #
@symptom_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_SYMPTOM")
def create():
    # Fix: Instantiate form object with parentheses
    form = SymptomCreateForm()

    if form.validate_on_submit():
        try:
            # Retrieve uploaded image file directly or via WTForms
            image_file = request.files.get("image") or form.image.data

            SymptomService.create_symptom(
                symptom_name=form.symptom_name.data,
                symptom_group=form.symptom_group.data,
                description=form.description.data,
                is_active=form.is_active.data,
                image_file=image_file,
            )
            flash("Symptom created successfully!", "success")
            return redirect(url_for("tbl_symptoms.index"))
        except ValueError as ve:
            flash(str(ve), "danger")
        except Exception as e:
            logger.error(f"Error creating symptom: {e}")
            flash("Failed to create symptom.", "danger")

    return render_template("symptom_page/create.html", form=form)


# ---------- EDIT ---------- #
@symptom_bp.route("/<int:symptom_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("EDIT_SYMPTOM")
def edit(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)

    # Combine request.form and request.files so WTForms captures file uploads
    formdata = CombinedMultiDict([request.form, request.files]) if request.method == "POST" else None

    form = SymptomEditForm(
        formdata=formdata,
        obj=symptom,
        original_symptom=symptom,
    )

    if form.validate_on_submit():
        try:
            data = {
                "symptom_name": form.symptom_name.data,
                "symptom_group": form.symptom_group.data,
                "description": form.description.data,
                "is_active": form.is_active.data,
            }

            # Capture image from form or request.files
            image_file = form.image.data or request.files.get("image")

            updated_symptom = SymptomService.update_symptom(
                symptom_id=symptom.id,
                data=data,
                image_file=image_file,
            )

            flash(
                f"Symptom '{updated_symptom.symptom_name}' was updated successfully.",
                "success",
            )
            return redirect(
                url_for("tbl_symptoms.detail", symptom_id=updated_symptom.id)
            )
        except ValueError as ve:
            flash(str(ve), "danger")
        except Exception as e:
            logger.error(f"Symptom Edit Error: {e}")
            flash("Failed to update symptom.", "danger")

    return render_template(
        "symptom_page/edit.html", form=form, symptom=symptom
    )


# ---------- DELETE CONFIRM ---------- #
@symptom_bp.route("/<int:symptom_id>/delete", methods=["GET"])
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_SYMPTOM")
def delete_confirm(symptom_id: int):
    try:
        symptom = SymptomService.get_symptom_by_id(symptom_id)
        if symptom is None:
            abort(404)
        form = SymptomConfirmDeleteForm(symptom_to_delete=symptom)
        return render_template(
            "symptom_page/delete_confirm.html", form=form, symptom=symptom
        )
    except Exception as e:
        logger.error(f"Symptom Delete Confirm Error: {e}")
        flash("Can't load delete confirmation page.", "danger")
        return redirect(url_for("tbl_symptoms.index"))


# ---------- DELETE EXECUTE ---------- #
@symptom_bp.route("/<int:symptom_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_SYMPTOM")
def delete(symptom_id: int):
    try:
        SymptomService.delete_symptom(symptom_id)
        flash("Symptom was deleted successfully.", "success")
    except ValueError as ve:
        flash(str(ve), "danger")
    except Exception as e:
        logger.error(f"Symptom Delete Error: {e}")
        flash("Failed to delete symptom.", "danger")

    return redirect(url_for("tbl_symptoms.index"))