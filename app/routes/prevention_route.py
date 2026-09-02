from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from werkzeug.datastructures import FileStorage

from app.forms.prevention_form import PreventionCreateForm, PreventionEditForm, PreventionConfirmDeleteForm, disease_choices
from app.services.prevention_service import PreventionService
from app.models.diseases import DiseaseTable
from app.decorators.access import role_required, permission_required

prevention_bp = Blueprint("prevention", __name__, url_prefix="/admin/preventions")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif'}

@prevention_bp.route("/")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_PREVENTION")
def index():
    preventions = PreventionService.get_all()
    return render_template("prevention_page/index.html", preventions=preventions)

@prevention_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_PREVENTION")
def create():
    form = PreventionCreateForm()
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            image_file = form.image.data
            PreventionService.create({
                "disease_id": form.disease_id.data,
                "prevention_type": form.prevention_type.data,
                "method": form.method.data,
                "description": form.description.data,
                "priority": form.priority.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Prevention created successfully.", "success")
            return redirect(url_for("prevention.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("prevention_page/create.html", form=form)

@prevention_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("EDIT_PREVENTION")
def edit(id):
    prevention = PreventionService.get_by_id(id)
    form = PreventionEditForm(obj=prevention)
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if request.method == "GET":
        form.disease_id.data = prevention.disease_id
        form.prevention_type.data = prevention.prevention_type
        form.method.data = prevention.method
        form.description.data = prevention.description
        form.priority.data = prevention.priority
        form.is_active.data = prevention.is_active

    if form.validate_on_submit():
        try:
            image_file = form.image.data if isinstance(form.image.data, FileStorage) else None
            PreventionService.update(prevention, {
                "disease_id": form.disease_id.data,
                "prevention_type": form.prevention_type.data,
                "method": form.method.data,
                "description": form.description.data,
                "priority": form.priority.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Prevention updated successfully.", "success")
            return redirect(url_for("prevention.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("prevention_page/edit.html", form=form, prevention=prevention)

@prevention_bp.route("/<int:id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("DETAIL_PREVENTION")
def detail(id):
    prevention = PreventionService.get_by_id(id)
    return render_template("prevention_page/detail.html", prevention=prevention)

@prevention_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_PREVENTION")
def delete(id):
    prevention = PreventionService.get_by_id(id)
    form = PreventionConfirmDeleteForm()

    if form.validate_on_submit():
        try:
            PreventionService.delete(prevention)
            flash("Prevention deleted successfully.", "success")
            return redirect(url_for("prevention.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("prevention_page/delete_confirm.html", form=form, prevention=prevention)

@prevention_bp.route('/api/preventions/all', methods=['GET'])
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_PREVENTION")
def get_all_preventions():
    try:
        # Fetch all records via your service layer
        preventions = PreventionService.get_all()
        
        data = []
        for p in preventions:
            # Safely extract disease name from the relationship (DiseaseTable)
            disease_name = "N/A"
            if hasattr(p, 'disease') and p.disease:
                disease_name = getattr(p.disease, 'disease_name', 'N/A')
            elif hasattr(p, 'disease_name'):
                disease_name = p.disease_name or "N/A"

            data.append({
                "id": p.id,
                "disease": disease_name,
                "type": getattr(p, 'prevention_type', ''),
                "method": getattr(p, 'method', '') or "",
                "description": getattr(p, 'description', '') or "",
                "priority": f"Priority {getattr(p, 'priority', 1)}",
                "status": "Active" if getattr(p, 'is_active', True) else "Inactive"
            })
            
        return jsonify(data), 200

    except Exception as e:
        print(f"Error fetching preventions for PDF export: {str(e)}")
        return jsonify({"error": "Failed to fetch database records", "details": str(e)}), 500