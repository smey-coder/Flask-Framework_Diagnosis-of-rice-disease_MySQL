from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from app.models.growth_stage import GrowthStageTable
from extensions import db
from flask_login import login_required, current_user
from app.services.treatment_history_service import (TreatmentHistoryService)
from app.models.treatment_histories import (TreatmentHistoryTable)
from app.models.diagnosis_history import (DiagnosisHistoryTable)
from app.models.treatments import (TreatmentTable)
from app.models.crop_monitoring import (CropMonitoringTable)
from app.forms.treatment_history_form import (TreatmentHistoryForm)

from app.decorators.access import role_required, permission_required
# ============================================================
# BLUEPRINT
# ============================================================

treatment_history_bp = Blueprint("treatment_history",__name__,url_prefix="/admin/treatment-histories")


# ============================================================
# INDEX
# ============================================================

@treatment_history_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin","Expert")
@permission_required("VIEW_TREATMENT_HISTORY")
def index():
    try:
        # ----------------------------------------------------
        # Query Parameters
        # ----------------------------------------------------
        page = request.args.get("page", 1,type=int)
        monitoring_id = request.args.get("monitoring_id",type=int)
        diagnosis_history_id = request.args.get("diagnosis_history_id",type=int)
        status = request.args.get("status","",type=str).strip()
        search = request.args.get("search","",type=str).strip()
        # Create lookup dictionary: { 1: <GrowthStage 1>, 2: <GrowthStage 2> }
        stages_map = {stage.id: stage for stage in GrowthStageTable.query.all()}
    
        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------
        pagination = TreatmentHistoryService.paginate(
            page=page,
            per_page=10,
            user_id=current_user.id,
            monitoring_id=monitoring_id,
            diagnosis_history_id=diagnosis_history_id,
            status=status if status else None,
            search=search if search else None
        )


        # ----------------------------------------------------
        # Check Pagination
        # ----------------------------------------------------

        if pagination is None:
            flash("Unable to load treatment histories.","danger")
            return redirect(url_for("admin.dashboard"))

        # ----------------------------------------------------
        # History List
        # ----------------------------------------------------

        histories = pagination.items


        # ----------------------------------------------------
        # Status Choices
        # ----------------------------------------------------

        status_choices = [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed")
        ]


        # ----------------------------------------------------
        # Render
        # ----------------------------------------------------

        return render_template(
            "admin_page/treatment_history_page/index.html",

            histories=histories,

            pagination=pagination,

            monitoring_id=monitoring_id,

            diagnosis_history_id=diagnosis_history_id,

            status=status,

            search=search,

            stages_map=stages_map,

            status_choices=status_choices,

            user=current_user
        )


    except Exception as e:

        print(f"Treatment History Index Error: {e}")
        flash("An error occurred while loading treatment histories.","danger")
        return redirect(url_for("admin.dashboard"))
# ============================================================
# CREATE
# ============================================================

@treatment_history_bp.route("/create",methods=["GET", "POST"])
@login_required
@role_required("Admin","Expert")
@permission_required("CREATE_TREATMENT_HISTORY")
def create():
    try:

        # ----------------------------------------------------
        # GET Parameters
        # ----------------------------------------------------

        monitoring_id = request.args.get(
            "monitoring_id",
            type=int
        )

        diagnosis_history_id = request.args.get(
            "diagnosis_history_id",
            type=int
        )

        treatment_id = request.args.get(
            "treatment_id",
            type=int
        )


        # ----------------------------------------------------
        # Validate Monitoring
        # ----------------------------------------------------

        if not monitoring_id:

            flash(
                "Monitoring is required.",
                "warning"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # Validate Diagnosis
        # ----------------------------------------------------

        if not diagnosis_history_id:

            flash(
                "Diagnosis history is required.",
                "warning"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # Validate Treatment
        # ----------------------------------------------------

        if not treatment_id:

            flash(
                "Treatment is required.",
                "warning"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # Verify Monitoring
        # ----------------------------------------------------

        monitoring = (
            CropMonitoringTable.query
            .filter_by(
                id=monitoring_id
            )
            .first()
        )

        if not monitoring:

            flash(
                "Monitoring record not found.",
                "danger"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # Verify Diagnosis History
        # ----------------------------------------------------

        diagnosis = (
            DiagnosisHistoryTable.query
            .filter_by(
                id=diagnosis_history_id
            )
            .first()
        )

        if not diagnosis:

            flash(
                "Diagnosis history not found.",
                "danger"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # Verify Treatment
        # ----------------------------------------------------

        treatment = (
            TreatmentTable.query
            .filter_by(
                id=treatment_id
            )
            .first()
        )

        if not treatment:

            flash(
                "Treatment not found.",
                "danger"
            )

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # FORM
        # ----------------------------------------------------

        form = TreatmentHistoryForm()


        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if form.validate_on_submit():

            history = TreatmentHistoryService.create(

                monitoring_id=monitoring_id,

                diagnosis_history_id=diagnosis_history_id,

                treatment_id=treatment_id,

                treatment_date=form.treatment_date.data,

                status=form.status.data,

                result=form.result.data,

                notes=form.notes.data
            )


            # ------------------------------------------------
            # Create Failed
            # ------------------------------------------------

            if history is None:

                flash(
                    "Unable to create treatment history.",
                    "danger"
                )

                return render_template(
                    "admin_page/treatment_history_page/create.html",

                    form=form,

                    monitoring_id=monitoring_id,

                    diagnosis_history_id=diagnosis_history_id,

                    treatment_id=treatment_id,

                    monitoring=monitoring,

                    diagnosis=diagnosis,

                    treatment=treatment,

                    user=current_user
                )


            # ------------------------------------------------
            # Success
            # ------------------------------------------------

            flash(
                "Treatment history created successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "treatment_history.detail",
                    id=history.id
                )
            )


        # ----------------------------------------------------
        # GET / Validation Error
        # ----------------------------------------------------

        return render_template(
            "admin_page/treatment_history_page/create.html",

            form=form,

            monitoring_id=monitoring_id,

            diagnosis_history_id=diagnosis_history_id,

            treatment_id=treatment_id,

            monitoring=monitoring,

            diagnosis=diagnosis,

            treatment=treatment,

            user=current_user
        )


    except Exception as e:

        print(
            f"Treatment History Create Error: {e}"
        )

        flash(
            "An error occurred while creating treatment history.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


# ============================================================
# DETAIL
# ============================================================

@treatment_history_bp.route("/<int:id>",methods=["GET"])
@login_required
@role_required("Admin","Expert")
@permission_required("DETAIL_TREATMENT_HISTORY")
def detail(id):

    try:

        # ----------------------------------------------------
        # Get History
        # ----------------------------------------------------

        history = TreatmentHistoryService.get_by_id(id)


        if not history:

            flash(
                "Treatment history not found.",
                "warning"
            )

            return redirect(
                url_for(
                    "treatment_history.index"
                )
            )


        # ----------------------------------------------------
        # Render
        # ----------------------------------------------------

        return render_template(
            "admin_page/treatment_history_page/detail.html",

            history=history,

            user=current_user
        )


    except Exception as e:

        print(
            f"Treatment History Detail Error: {e}"
        )

        flash(
            "Unable to load treatment history details.",
            "danger"
        )

        return redirect(
            url_for(
                "treatment_history.index"
            )
        )


# ============================================================
# EDIT
# ============================================================

@treatment_history_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin","Expert")
@permission_required("EDIT_TREATMENT_HISTORY")
def edit(id):

    try:

        # =====================================================
        # GET HISTORY
        # =====================================================

        history = TreatmentHistoryService.get_by_id(id)

        if not history:

            flash(
                "Treatment history not found.",
                "warning"
            )

            return redirect(
                url_for("treatment_history.index")
            )


        # =====================================================
        # CREATE FORM
        # =====================================================

        form = TreatmentHistoryForm()


        # =====================================================
        # GET
        # =====================================================

        if request.method == "GET":

            form.treatment_date.data = (
                history.treatment_date
            )

            form.status.data = (
                history.status
            )

            form.result.data = (
                history.result or ""
            )

            form.notes.data = (
                history.notes or ""
            )


        # =====================================================
        # POST
        # =====================================================

        if form.validate_on_submit():

            updated_history = (
                TreatmentHistoryService.update(
                    history=history,
                    treatment_date=form.treatment_date.data,
                    status=form.status.data,
                    result=form.result.data,
                    notes=form.notes.data
                )
            )

            if updated_history:

                flash(
                    "Treatment history updated successfully.",
                    "success"
                )

                return redirect(
                    url_for(
                        "treatment_history.detail",
                        id=history.id
                    )
                )

            flash(
                "Unable to update treatment history.",
                "danger"
            )


        # =====================================================
        # RENDER
        # =====================================================

        return render_template(
            "admin_page/treatment_history_page/edit.html",

            history=history,

            form=form,

            user=current_user
        )


    except Exception as e:


        print(
            f"Treatment History Edit Error: {e}"
        )

        flash(
            "Unable to edit treatment history.",
            "danger"
        )

        return redirect(
            url_for(
                "treatment_history.index"
            )
        )


# ============================================================
# DELETE
# ============================================================

@treatment_history_bp.route("/<int:id>/delete",methods=["GET", "POST"])
@login_required
@role_required("Admin","Expert")
@permission_required("DELETE_TREATMENT_HISTORY")
def delete(id):

    try:

        history = TreatmentHistoryService.get_by_id(id)

        if not history:

            flash(
                "Treatment history not found.",
                "warning"
            )

            return redirect(
                url_for("treatment_history.index")
            )

        if request.method == "POST":

            success = TreatmentHistoryService.delete(history)

            if success:

                flash(
                    "Treatment history deleted successfully.",
                    "success"
                )

                return redirect(
                    url_for("treatment_history.index")
                )

            flash(
                "Unable to delete treatment history.",
                "danger"
            )

        return render_template(
            "admin_page/treatment_history_page/delete.html",
            history=history,
            user=current_user
        )

    except Exception as e:
        print(f"Treatment History Delete Error: {e}")
        db.session.rollback()
        flash("An error occurred while deleting treatment history.","danger")
        return redirect(url_for("treatment_history.index"))

