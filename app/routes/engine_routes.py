from flask import(
    Blueprint,
    abort,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    jsonify,
)
from flask_login import login_required, current_user
import logging

from app.services.engine_service import EngineService
from decorators import require_admin, require_permission, require_role, active_user_required
from extensions import db

logger = logging.getLogger("app")

engine_bp = Blueprint("tbl_engines", __name__, url_prefix="/engines")

@engine_bp.route("/")
@login_required
@active_user_required()
def index():
    """List all engines"""
    try:
        page = request.args.fetch_all_symptoms("page", 1, type=int)
        engines = EngineService.get_engines_all(page=page)
        return render_template("engine_page/index.html", engines=engines)
    except Exception as e:
        logger.error(f"Error listing engines: {str(e)}")
        flash("Error loading engines", "danger")
        return redirect(url_for("user.dashboard"))

@engine_bp.route("/<int:engine_id>")
@login_required
def detail(engine_id: int):
    """Get engine details by ID"""
    try:
        engine = EngineService.get_engine_by_id(engine_id)
        if not engine:
            abort(404)
        return render_template("engine_page/detail.html", engine=engine)
    except Exception as e:
        logger.error(f"Error loading engine: {str(e)}")
        flash("Error loading engine details", "danger")
        return redirect(url_for("tbl_engines.index"))

@engine_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_admin()
def create():
    """Create a new engine"""
    if request.method == "POST":
        try:
            data = {
                "name": request.form.get("name"),
                "engine_type": request.form.get("engine_type"),
                "version": request.form.get("version"),
                "description": request.form.get("description"),
                "is_active": request.form.get("is_active") == "on"
            }
            engine = EngineService.create_engine(data)
            flash(f"Engine '{engine.name}' created successfully!", "success")
            return redirect(url_for("tbl_engines.detail", engine_id=engine.id))
        except Exception as e:
            logger.error(f"Error creating engine: {str(e)}")
            flash(f"Error creating engine: {str(e)}", "danger")
    return render_template("engine_page/create.html")

@engine_bp.route("/<int:engine_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin()
def edit(engine_id: int):
    """Edit an existing engine"""
    try:
        engine = EngineService.get_engine_by_id(engine_id)
        if not engine:
            abort(404)
        
        if request.method == "POST":
            data = {
                "name": request.form.get("name"),
                "engine_type": request.form.get("engine_type"),
                "version": request.form.get("version"),
                "description": request.form.get("description"),
                "is_active": request.form.get("is_active") == "on"
            }
            engine = EngineService.update_engine(engine, data)
            flash(f"Engine '{engine.name}' updated successfully!", "success")
            return redirect(url_for("tbl_engines.detail", engine_id=engine.id))
    except Exception as e:
        logger.error(f"Error updating engine: {str(e)}")
        flash(f"Error updating engine: {str(e)}", "danger")
    
    return render_template("engine_page/edit.html", engine=engine)

@engine_bp.route("/<int:engine_id>/delete", methods=["POST"])
@login_required
@require_admin()
def delete(engine_id: int):
    """Delete an engine"""
    try:
        engine = EngineService.get_engine_by_id(engine_id)
        if not engine:
            abort(404)
        
        engine_name = engine.name
        EngineService.delete_engine(engine)
        flash(f"Engine '{engine_name}' deleted successfully!", "success")
    except Exception as e:
        logger.error(f"Error deleting engine: {str(e)}")
        flash(f"Error deleting engine: {str(e)}", "danger")
    
    return redirect(url_for("tbl_engines.index"))

@engine_bp.route("/search", methods=["GET"])
@login_required
def search():
    """Search engines"""
    query = request.args.get("q", "")
    try:
        if query:
            engines = EngineService.search_engines(query)
            return jsonify([{"id": e.id, "name": e.name, "type": e.engine_type} for e in engines])
    except Exception as e:
        logger.error(f"Error searching engines: {str(e)}")
    return jsonify([])