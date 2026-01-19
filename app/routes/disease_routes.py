from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    jsonify,
)
from flask_login import login_required, current_user
import logging

from app.forms.diseases import (
    DiseaseCreateForm,
    DiseaseEditForm,
    DiseaseConfirmDeleteForm,
    DiseaseSearchForm,
)
from app.services.disease_service import DiseaseService
from app.models.diseases import DiseaseTable
from decorators import require_admin, require_permission, require_role, active_user_required
from extensions import db

logger = logging.getLogger("app")

disease_bp = Blueprint("tbl_diseases", __name__, url_prefix="/diseases")



@disease_bp.route("/")
@login_required
@active_user_required()
def index():
    """List all diseases with search functionality"""
    try:
        page = request.args.get("page", 1, type=int)
        search_form = DiseaseSearchForm(request.args, meta={"csrf_enabled": False})
        
        # Get search parameters
        disease_name = request.args.get("disease_name", "").strip()
        disease_type = request.args.get("disease_type", "").strip()
        severity_level = request.args.get("severity_level", "").strip()
        
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
            search_form=search_form,
            current_user=current_user
        )
    except Exception as e:
        logger.error(f"Error listing diseases: {e}")
        flash("An error occurred while loading diseases.", "danger")
        return redirect(url_for("user.dashboard"))


@disease_bp.route("/<int:disease_id>")
@login_required
@active_user_required()
def detail(disease_id: int):
    """View disease details"""
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if disease is None:
            flash("Disease not found.", "warning")
            abort(404)
        
        return render_template(
            "disease_page/detail.html",
            disease=disease,
            current_user=current_user
        )
    except Exception as e:
        logger.error(f"Error retrieving disease detail {disease_id}: {e}")
        flash("An error occurred while loading disease details.", "danger")
        abort(404)


@disease_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_admin()
def create():
    """Create a new disease"""
    try:
        form = DiseaseCreateForm()
        
        if form.validate_on_submit():
            data = {
                "disease_name": form.disease_name.data.strip(),
                "disease_type": form.disease_type.data.strip(),
                "description": form.description.data.strip() if form.description.data else "",
                "severity_level": form.severity_level.data.strip() if form.severity_level.data else "Low",
                "image": form.image.data if form.image.data else None,
                "is_active": form.is_active.data,
            }
            
            # Validate required fields
            if not data["disease_name"]:
                flash("Disease name is required.", "danger")
                return render_template("disease_page/create.html", form=form)
            
            if not data["disease_type"]:
                flash("Disease type is required.", "danger")
                return render_template("disease_page/create.html", form=form)
            
            disease = DiseaseService.create_disease(data)
            
            if disease:
                flash(f"Disease '{disease.disease_name}' was created successfully.", "success")
                logger.info(f"Disease created: {disease.disease_name} (ID: {disease.id}) by {current_user.username}")
                return redirect(url_for("tbl_diseases.detail", disease_id=disease.id))
            else:
                flash("Failed to create disease. Please try again.", "danger")
        
        return render_template("disease_page/create.html", form=form)
    
    except Exception as e:
        logger.error(f"Error creating disease: {e}")
        flash("An error occurred while creating the disease.", "danger")
        return render_template("disease_page/create.html", form=form)


@disease_bp.route("/<int:disease_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin()
def edit(disease_id: int):
    """Edit an existing disease"""
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if disease is None:
            flash("Disease not found.", "warning")
            abort(404)
        
        form = DiseaseEditForm(disease)
        
        if form.validate_on_submit():
            data = {
                "disease_name": form.disease_name.data.strip(),
                "disease_type": form.disease_type.data.strip(),
                "description": form.description.data.strip() if form.description.data else "",
                "severity_level": form.severity_level.data.strip() if form.severity_level.data else "Low",
                "image": form.image.data if form.image.data else disease.image,
                "is_active": form.is_active.data,
            }
            
            # Validate required fields
            if not data["disease_name"]:
                flash("Disease name is required.", "danger")
                return render_template("disease_page/edit.html", form=form, disease=disease)
            
            if not data["disease_type"]:
                flash("Disease type is required.", "danger")
                return render_template("disease_page/edit.html", form=form, disease=disease)
            
            updated_disease = DiseaseService.update_disease(disease_id, data)
            
            if updated_disease:
                flash(f"Disease '{updated_disease.disease_name}' was updated successfully.", "success")
                logger.info(f"Disease updated: {updated_disease.disease_name} (ID: {disease_id}) by {current_user.username}")
                return redirect(url_for("tbl_diseases.detail", disease_id=disease_id))
            else:
                flash("Failed to update disease. Please try again.", "danger")
        
        return render_template("disease_page/edit.html", form=form, disease=disease)
    
    except Exception as e:
        logger.error(f"Error editing disease {disease_id}: {e}")
        flash("An error occurred while editing the disease.", "danger")
        return render_template("disease_page/edit.html", form=form, disease=disease)


@disease_bp.route("/<int:disease_id>/delete", methods=["GET", "POST"])
@login_required
@require_admin()
def delete(disease_id: int):
    """Delete a disease"""
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if disease is None:
            flash("Disease not found.", "warning")
            abort(404)
        
        form = DiseaseConfirmDeleteForm()
        
        if form.validate_on_submit():
            disease_name = disease.disease_name
            
            # Check if disease is associated with other records
            if disease.symptoms or disease.treatments or disease.preventions:
                flash(
                    f"Cannot delete '{disease_name}' because it is associated with symptoms, treatments, or preventions. "
                    "Please remove these associations first.",
                    "danger"
                )
                return render_template("disease_page/delete_confirm.html", disease=disease, form=form)
            
            DiseaseService.delete_disease(disease_id)
            flash(f"Disease '{disease_name}' was deleted successfully.", "success")
            logger.info(f"Disease deleted: {disease_name} (ID: {disease_id}) by {current_user.username}")
            return redirect(url_for("tbl_diseases.index"))
        
        return render_template("disease_page/delete_confirm.html", disease=disease, form=form)
    
    except Exception as e:
        logger.error(f"Error deleting disease {disease_id}: {e}")
        flash("An error occurred while deleting the disease.", "danger")
        return render_template("disease_page/delete_confirm.html", disease=disease, form=form)


# ===================== API ENDPOINTS =====================

@disease_bp.route("/api/<int:disease_id>/json")
@login_required
def get_disease_json(disease_id: int):
    """Get disease details as JSON"""
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if disease is None:
            return jsonify({"error": "Disease not found"}), 404
        
        return jsonify({
            "id": disease.id,
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "is_active": disease.is_active,
            "created_at": disease.created_at.isoformat() if hasattr(disease, 'created_at') else None,
        })
    except Exception as e:
        logger.error(f"Error fetching disease JSON {disease_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@disease_bp.route("/api/search")
@login_required
def search_diseases_api():
    """Search diseases via API"""
    try:
        disease_name = request.args.get("name", "").strip()
        disease_type = request.args.get("type", "").strip()
        page = request.args.get("page", 1, type=int)
        
        diseases = DiseaseService.search_diseases(
            disease_name=disease_name if disease_name else None,
            disease_type=disease_type if disease_type else None,
            page=page,
            per_page=20
        )
        
        return jsonify({
            "total": diseases.total,
            "pages": diseases.pages,
            "current_page": page,
            "diseases": [
                {
                    "id": d.id,
                    "disease_name": d.disease_name,
                    "disease_type": d.disease_type,
                    "severity_level": d.severity_level,
                }
                for d in diseases.items
            ]
        })
    except Exception as e:
        logger.error(f"Error searching diseases API: {e}")
        return jsonify({"error": "Internal server error"}), 500
