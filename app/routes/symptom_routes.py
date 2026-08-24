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
# from decorators import require_admin, require_permission, require_role, active_user_required
from app.decorators.access import role_required, permission_required
from extensions import db

logger = logging.getLogger("app")

symptom_bp = Blueprint("tbl_symptoms", __name__, url_prefix="/symptoms")

@symptom_bp.route("/")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_SYMPTOM")
def index():
    try:
        symptoms = SymptomService.get_symptom_all()
        return render_template("symptom_page/index.html", symptoms=symptoms)
    except Exception as e:
        print(f"Symptom Load error: {e}")
        flash("Can't load symptom", "danger")
        return redirect(url_for("admin.dashboard"))

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
        print(f"Symptom Detail Error: {e}")
        flash("An error  detail symptom.","danger")
        return redirect(url_for("tbl_symptoms.index"))


@symptom_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_SYMPTOM")
def create():
    try:
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
    except Exception as e:
        print(f"Error: {e}")
        flash("Can't create symptom", "danger")
        return redirect(url_for("tbl_symptoms.index"))
    

@symptom_bp.route("/<int:symptom_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("EDIT_SYMPTOM")
def edit(symptom_id: int):
    try:
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
    except Exception as e:
        print(f"Error: {e}")
        flash("Can't update symptom", "danger")
        return redirect(url_for("tbl_symptoms"))
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
        return render_template("symptom_page/delete_confirm.html", form=form, symptom=symptom)
    except Exception as e:
        print(f"Error: {e}")
        flash("Can't delete confirm.", "danger")
        return redirect(url_for("tbl_symptoms.index"))
    

@symptom_bp.route("/<int:symptom_id>/delete", methods=["POST"])
@login_required
def delete(symptom_id: int):
    try:
        symptom = SymptomService.get_symptom_by_id(symptom_id)
        if symptom is None:
            abort(404)
        
        SymptomService.delete_symptom(symptom)
        flash(f"Symptom '{symptom.symptom_name}' was deleted successfully.", "success")
        return redirect(url_for("tbl_symptoms.index")) 
    except Exception as e:
        print(f"Error: {e}")
        flash("Can't delete confirm.", "danger")
        return redirect(url_for("tbl_symptoms.index"))