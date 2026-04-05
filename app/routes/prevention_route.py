from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from werkzeug.datastructures import FileStorage

from app.forms.prevention_form import PreventionCreateForm, PreventionEditForm, PreventionConfirmDeleteForm, disease_choices
from app.services.prevention_service import PreventionService
from app.models.diseases import DiseaseTable

prevention_bp = Blueprint("prevention", __name__, url_prefix="/admin/preventions")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif'}

@prevention_bp.route("/")
@login_required
def index():
    preventions = PreventionService.get_all()
    return render_template("prevention_page/index.html", preventions=preventions)

@prevention_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = PreventionCreateForm()
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            image_file = form.image.data
            PreventionService.create({
                "disease_id": form.disease_id.data,
                "prevention_type": form.prevention_type.data,
                "description": form.description.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Prevention created successfully.", "success")
            return redirect(url_for("prevention.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("prevention_page/create.html", form=form)

@prevention_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    prevention = PreventionService.get_by_id(id)
    form = PreventionEditForm(obj=prevention)
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if request.method == "GET":
        form.disease_id.data = prevention.disease_id
        form.prevention_type.data = prevention.prevention_type
        form.description.data = prevention.description
        form.is_active.data = prevention.is_active

    if form.validate_on_submit():
        try:
            image_file = form.image.data if isinstance(form.image.data, FileStorage) else None
            PreventionService.update(prevention, {
                "disease_id": form.disease_id.data,
                "prevention_type": form.prevention_type.data,
                "description": form.description.data,
                "is_active": form.is_active.data
            }, image_file)
            flash("Prevention updated successfully.", "success")
            return redirect(url_for("prevention.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("prevention_page/edit.html", form=form, prevention=prevention)

@prevention_bp.route("/<int:id>")
@login_required
def detail(id):
    prevention = PreventionService.get_by_id(id)
    return render_template("prevention_page/detail.html", prevention=prevention)

@prevention_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
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
