from flask import(
    Blueprint,
    abort,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    request,
    jsonify,
)
from flask_login import login_required, current_user
import logging

from app.forms.symptom_forms import (
    SymptomCreateForm,
    SymptomEditForm,
    SymptomConfirmDeleteForm,
    SymptomSearchForm,
)
from app.services.symptom_service import SymptomService
from app.models.symptoms import SymptomsTable
from decorators import require_admin, require_permission, require_role, active_user_required
from extensions import db

logger = logging.getLogger("app")

symptom_bp = Blueprint("tbl_symptoms", __name__, url_prefix="/symptoms")

@symptom_bp.route("/")
@login_required
def index():
    symptoms = SymptomService.get_symptom_all()
    return render_template("symptom_page/index.html", symptoms=symptoms)

@symptom_bp.route("/<int:symptom_id>")
@login_required
def detail(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)
    return render_template("symptom_page/detail.html", symptom=symptom)

@symptom_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = SymptomCreateForm()
    if form.validate_on_submit():
        data = {
            "symptom_name": form.symptom_name.data,
            "symptom_group": form.symptom_group.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }
        symptom = SymptomService.create_symptom(data)
        flash(f"Symptom '{symptom.symptom_name}' was created successfully.", "success")
        return redirect(url_for("tbl_symptoms.index"))
    
    return render_template("symptom_page/create.html", form=form)

@symptom_bp.route("/<int:symptom_id>/edit", methods=["GET", "POST"])
@login_required
def edit(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)
    
    form = SymptomEditForm(original_symptom=symptom, obj=symptom)
    if form.validate_on_submit():
        data = {
            "symptom_name": form.symptom_name.data,
            "symptom_group": form.symptom_group.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }
        SymptomService.update_symptom(symptom, data)
        flash(f"Symptom '{symptom.symptom_name}' was updated successfully.", "success")
        return redirect(url_for("tbl_symptoms.detail", symptom_id=symptom.id))
    
    return render_template("symptom_page/edit.html", form=form, symptom=symptom)


@symptom_bp.route("/<int:symptom_id>/delete", methods=["GET"])
@login_required
def delete_confirm(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)

    form = SymptomConfirmDeleteForm(symptom_to_delete=symptom)
    return render_template("symptom_page/delete_confirm.html", form=form, symptom=symptom)

@symptom_bp.route("/<int:symptom_id>/delete", methods=["POST"])
@login_required
def delete(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)

    SymptomService.delete_symptom(symptom)
    flash(f"Symptom '{symptom.symptom_name}' was deleted successfully.", "success")
    return redirect(url_for("tbl_symptoms.index"))