from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
)
from flask_login import login_required, current_user
from functools import wraps

from app.forms.diseases import (
    DiseaseCreateForm,
    DiseaseEditForm,
    DiseaseConfirmDeleteForm,
    DiseaseSearchForm,
)
from app.services.disease_service import DiseaseService
from app.models.role import RoleTable


disease_bp = Blueprint("tbl_diseases", __name__, url_prefix="/diseases")


def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        if not current_user.has_role("Admin"):
            flash("You do not have permission to access this page.", "danger")
            abort(403)
        
        return fn(*args, **kwargs)
    return decorated_function


@disease_bp.route("/")
@login_required
def index():
    """List all diseases with search functionality"""
    page = request.args.get("page", 1, type=int)
    search_form = DiseaseSearchForm(request.args, meta={"csrf_enabled": False})
    
    # Get search parameters
    disease_name = request.args.get("disease_name", "")
    disease_type = request.args.get("disease_type", "")
    severity_level = request.args.get("severity_level", "")
    
    # Perform search
    diseases = DiseaseService.search_diseases(
        disease_name=disease_name if disease_name else None,
        disease_type=disease_type if disease_type else None,
        severity_level=severity_level if severity_level else None,
        page=page,
        per_page=10
    )
    
    return render_template(
        "disease_page/index.html",
        diseases=diseases,
        search_form=search_form
    )


@disease_bp.route("/<int:disease_id>")
@login_required
def detail(disease_id: int):
    """View disease details"""
    disease = DiseaseService.get_disease_by_id(disease_id)
    if disease is None:
        abort(404)
    
    return render_template("disease_page/detail.html", disease=disease)


@disease_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    """Create a new disease"""
    form = DiseaseCreateForm()
    
    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data,
            "disease_type": form.disease_type.data,
            "description": form.description.data,
            "severity_level": form.severity_level.data,
            "image": form.image.data,
            "is_active": form.is_active.data,
        }
        
        disease = DiseaseService.create_disease(data)
        flash(f"Disease '{disease.disease_name}' was created successfully.", "success")
        return redirect(url_for("tbl_diseases.detail", disease_id=disease.id))
    
    return render_template("disease_page/create.html", form=form)


@disease_bp.route("/<int:disease_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(disease_id: int):
    """Edit an existing disease"""
    disease = DiseaseService.get_disease_by_id(disease_id)
    if disease is None:
        abort(404)
    
    form = DiseaseEditForm(disease)
    
    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data,
            "disease_type": form.disease_type.data,
            "description": form.description.data,
            "severity_level": form.severity_level.data,
            "image": form.image.data,
            "is_active": form.is_active.data,
        }
        
        updated_disease = DiseaseService.update_disease(disease_id, data)
        flash(f"Disease '{updated_disease.disease_name}' was updated successfully.", "success")
        return redirect(url_for("tbl_diseases.detail", disease_id=disease_id))
    
    return render_template("disease_page/edit.html", form=form, disease=disease)


@disease_bp.route("/<int:disease_id>/delete", methods=["GET", "POST"])
@admin_required
def delete(disease_id: int):
    """Delete a disease"""
    disease = DiseaseService.get_disease_by_id(disease_id)
    if disease is None:
        abort(404)
    
    form = DiseaseConfirmDeleteForm()
    
    if form.validate_on_submit():
        disease_name = disease.disease_name
        DiseaseService.delete_disease(disease_id)
        flash(f"Disease '{disease_name}' was deleted successfully.", "success")
        return redirect(url_for("tbl_diseases.index"))
    
    return render_template("disease_page/delete_confirm.html", disease=disease, form=form)
