import os
from flask import (
    Blueprint,
    current_app,
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
from werkzeug.utils import secure_filename

from app.forms.diseases_forms import (
    DiseaseCreateForm,
    DiseaseEditForm,
    DiseaseConfirmDeleteForm,
    DiseaseSearchForm,
)
from app.services.disease_service import DiseaseService
from decorators import require_admin, active_user_required

logger = logging.getLogger("app")

disease_bp = Blueprint("tbl_diseases", __name__, url_prefix="/diseases")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ INDEX ------------------
@disease_bp.route("/")
@login_required
@active_user_required()
def index():
    """List all diseases with search functionality"""
    try:
        page = request.args.get("page", 1, type=int)
        search_form = DiseaseSearchForm(request.args, meta={"csrf_enabled": False})
        
        disease_name = request.args.get("disease_name", "").strip()
        disease_type = request.args.get("disease_type", "").strip()
        severity_level = request.args.get("severity_level", "").strip()
        
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


# ------------------ DETAIL ------------------
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


# ------------------ CREATE ------------------
@disease_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_admin()
def create():
    form = DiseaseCreateForm()
    
    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data.strip(),
            "disease_type": form.disease_type.data.strip(),
            "description": form.description.data.strip(),
            "severity_level": form.severity_level.data.strip(),
            "is_active": form.is_active.data
        }

        image_file = form.image.data if form.image.data else None

        try:
            disease = DiseaseService.create_disease(data, image_file)
            flash(f"Disease '{disease.disease_name}' created successfully.", "success")
            return redirect(url_for("tbl_diseases.index"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("An unexpected error occurred.", "danger")

    return render_template("disease_page/create.html", form=form)


# ------------------ EDIT ------------------
@disease_bp.route("/<int:disease_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin()
def edit(disease_id: int):
    disease = DiseaseService.get_disease_by_id(disease_id)
    if not disease:
        abort(404)

    # ✅ FIX HERE
    form = DiseaseEditForm(original_disease=disease, obj=disease)

    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data.strip(),
            "disease_type": form.disease_type.data.strip(),
            "description": form.description.data.strip() if form.description.data else "",
            "severity_level": form.severity_level.data.strip() if form.severity_level.data else "Low",
            "is_active": form.is_active.data
        }

        image_file = form.image.data if form.image.data and form.image.data.filename != "" else None

        try:
            DiseaseService.update_disease(disease_id, data, image_file)
            flash("Disease updated successfully.", "success")
            return redirect(url_for("tbl_diseases.detail", disease_id=disease_id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("disease_page/edit.html", form=form, disease=disease)


# ------------------ DELETE ------------------
@disease_bp.route("/<int:disease_id>/delete", methods=["GET", "POST"])
@login_required
@require_admin()
def delete(disease_id: int):
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if not disease:
            flash("Disease not found.", "warning")
            abort(404)

        form = DiseaseConfirmDeleteForm()

        # ✅ Handle POST request
        if request.method == "POST":
            disease_name = disease.disease_name

            # ✅ Check relationships (safe)
            if (disease.treatments and len(disease.treatments) > 0) or \
               (disease.preventions and len(disease.preventions) > 0):

                flash(
                    f"Cannot delete '{disease_name}' because it is associated with other data.",
                    "danger"
                )
                return render_template("disease_page/delete_confirm.html", disease=disease, form=form)

            try:
                DiseaseService.delete_disease(disease_id)

                flash(f"Disease '{disease_name}' deleted successfully.", "success")
                logger.info(f"Disease deleted: {disease_name} (ID: {disease_id}) by {current_user.username}")

                return redirect(url_for("tbl_diseases.index"))

            except Exception as e:
                logger.error(f"Delete error: {e}")
                flash(str(e), "danger")  # 🔥 show real error

        return render_template("disease_page/delete_confirm.html", disease=disease, form=form)

    except Exception as e:
        logger.error(f"Error deleting disease {disease_id}: {e}")
        flash(str(e), "danger")
        return render_template("disease_page/delete_confirm.html", disease=disease, form=form)


# ------------------ API ENDPOINTS ------------------
@disease_bp.route("/api/<int:disease_id>/json")
@login_required
def get_disease_json(disease_id: int):
    try:
        disease = DiseaseService.get_disease_by_id(disease_id)
        if not disease:
            return jsonify({"error": "Disease not found"}), 404
        
        return jsonify({
            "id": disease.id,
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "is_active": disease.is_active,
            "image_filename": getattr(disease, "image_filename", None),
            "created_at": disease.created_at.isoformat() if hasattr(disease, 'created_at') else None,
        })
    except Exception as e:
        logger.error(f"Error fetching disease JSON {disease_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@disease_bp.route("/api/search")
@login_required
def search_diseases_api():
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
                    "image_filename": getattr(d, "image_filename", None)
                }
                for d in diseases.items
            ]
        })
    except Exception as e:
        logger.error(f"Error searching diseases API: {e}")
        return jsonify({"error": "Internal server error"}), 500