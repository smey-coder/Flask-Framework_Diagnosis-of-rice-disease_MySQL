from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from werkzeug.datastructures import FileStorage

from app.forms.treatment_forms import TreatmentCreateForm, TreatmentEditForm, TreatmentConfirmDeleteForm, disease_choices
from app.services.treatment_service import TreatmentService
from app.models.diseases import DiseaseTable

treatment_bp = Blueprint("treatment", __name__, url_prefix="/admin/treatments")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif'}

@treatment_bp.route("/")
@login_required
def index():
    treatments = TreatmentService.get_all()
    return render_template("treatment_page/index.html", treatments=treatments)

@treatment_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TreatmentCreateForm()
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            image_file = form.image.data
            TreatmentService.create({
                "disease_id": form.disease_id.data,
                "treatment_type": form.treatment_type.data,
                "description": form.description.data,
                "method": form.method.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Treatment created successfully.", "success")
            return redirect(url_for("treatment.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("treatment_page/create.html", form=form)

@treatment_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    treatment = TreatmentService.get_by_id(id)
    form = TreatmentEditForm(obj=treatment)
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if request.method == "GET":
        form.disease_id.data = treatment.disease_id
        form.treatment_type.data = treatment.treatment_type
        form.description.data = treatment.description
        form.method.data = treatment.method
        form.is_active.data = treatment.is_active

    if form.validate_on_submit():
        try:
            image_file = form.image.data if isinstance(form.image.data, FileStorage) else None
            TreatmentService.update(treatment, {
                "disease_id": form.disease_id.data,
                "treatment_type": form.treatment_type.data,
                "description": form.description.data,
                "method": form.method.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Treatment updated successfully.", "success")
            return redirect(url_for("treatment.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("treatment_page/edit.html", form=form, treatment=treatment)

@treatment_bp.route("/<int:id>")
@login_required
def detail(id):
    treatment = TreatmentService.get_by_id(id)
    return render_template("treatment_page/detail.html", treatment=treatment)

@treatment_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete(id):
    treatments = TreatmentService.get_by_id(id)
    form = TreatmentConfirmDeleteForm()

    if form.validate_on_submit():
        try:
            TreatmentService.delete(treatments)
            flash("Treatment deleted successfully.", "success")
            return redirect(url_for("treatment.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("treatment_page/delete_confirm.html", form=form, treatments=treatments)
