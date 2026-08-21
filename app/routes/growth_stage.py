from flask import (
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_required
)

from app.forms.growth_stage_form import GrowthStageForm
from app.services.growth_stage_service import GrowthStageService

from app.decorators.access import permission_required, role_required


growth_stage_bp = Blueprint("growth_stage",__name__,url_prefix="/growth-stages")

# =========================================================
# INDEX
# =========================================================

@growth_stage_bp.route("/")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_GROWTH_STAGE")
def index():

    try:

        growth_stages = GrowthStageService.get_all()

        return render_template(
            "growth_stages/index.html",
            growth_stages=growth_stages
        )

    except Exception as e:

        flash(
            "Unable to load growth stages.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )


# =========================================================
# CREATE
# =========================================================

@growth_stage_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_GROWTH_STAGE")
def create():

    form = GrowthStageForm()

    if form.validate_on_submit():

        try:

            growth_stage, error = GrowthStageService.create(
                stage_name=form.stage_name.data.strip(),
                stage_name_kh=(
                    form.stage_name_kh.data.strip()
                    if form.stage_name_kh.data
                    else None
                ),
                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),
                stage_order=form.stage_order.data,
                status=form.status.data
            )

            if error:
                flash(error,"danger")
                return render_template(
                    "growth_stages/create.html",
                    form=form,
                    growth_stage = growth_stage
                )

            flash(
                "Growth stage created successfully.",
                "success"
            )

            return redirect(
                url_for("growth_stage.index")
            )

        except Exception as e:
            print(f"Errr: {e}")
            flash(
                "An unexpected error occurred.",
                "danger"
            )

    return render_template(
        "growth_stages/create.html",
        form=form,
        form_action=url_for("growth_stage.create"),
        cancel_url=url_for("growth_stage.index")
    )


# =========================================================
# DETAIL
# =========================================================

@growth_stage_bp.route("/<int:stage_id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_GROWTH_STAGE")
def detail(stage_id):

    try:

        growth_stage = GrowthStageService.get_by_id(
            stage_id
        )

        if not growth_stage:
            abort(404)

        return render_template(
            "growth_stages/detail.html",
            growth_stage=growth_stage
        )

    except Exception:

        flash(
            "Unable to load growth stage.",
            "danger"
        )

        return redirect(
            url_for("growth_stage.index")
        )


# =========================================================
# EDIT
# =========================================================

@growth_stage_bp.route(
    "/<int:stage_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin", "Expert")
@permission_required("UPDATE_GROWTH_STAGE")
def edit(stage_id):

    form = GrowthStageForm()

    try:

        # =================================================
        # GET GROWTH STAGE
        # =================================================

        growth_stage = GrowthStageService.get_by_id(
            stage_id
        )

        if not growth_stage:
            abort(404)

        # =================================================
        # LOAD FORM DATA
        # =================================================

        form = GrowthStageForm(
            obj=growth_stage
        )

        # =================================================
        # VALIDATE FORM
        # =================================================

        if form.validate_on_submit():

            # ---------------------------------------------
            # CLEAN DATA
            # ---------------------------------------------

            stage_name = (
                form.stage_name.data.strip()
            )

            stage_name_kh = (
                form.stage_name_kh.data.strip()
                if form.stage_name_kh.data
                else None
            )

            description = (
                form.description.data.strip()
                if form.description.data
                else None
            )

            stage_order = form.stage_order.data

            status = form.status.data

            # ---------------------------------------------
            # UPDATE
            # ---------------------------------------------

            success, error = GrowthStageService.update(

                growth_stage=growth_stage,

                stage_name=stage_name,

                stage_name_kh=stage_name_kh,

                stage_order=stage_order,

                description=description,

                status=status
            )

            # ---------------------------------------------
            # UPDATE FAILED
            # ---------------------------------------------

            if not success:

                flash(
                    error,
                    "danger"
                )

                return render_template(
                    "growth_stages/edit.html",
                    form=form,
                    growth_stage=growth_stage
                )

            # ---------------------------------------------
            # UPDATE SUCCESS
            # ---------------------------------------------

            flash(
                "Growth stage updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "growth_stage.detail",
                    stage_id=growth_stage.id
                )
            )

        # =================================================
        # GET REQUEST / VALIDATION FAILED
        # =================================================

        return render_template(
            "growth_stages/edit.html",
            form=form,
            growth_stage=growth_stage
        )

    except Exception as e:

        print(
            f"GrowthStage edit route error: {e}"
        )

        flash(
            "Unable to update growth stage.",
            "danger"
        )

        return redirect(
            url_for(
                "growth_stage.index"
            )
        )

# =========================================================
# DELETE CONFIRM
# =========================================================

@growth_stage_bp.route(
    "/<int:stage_id>/delete",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_GROWTH_STAGE")
def delete_confirm(stage_id):

    try:
        growth_stage = GrowthStageService.get_by_id(stage_id)

        if not growth_stage:
            abort(404)
        if request.method == "POST":
            success, error = GrowthStageService.delete(
                growth_stage
            )

            if not success:

                flash(
                    error,
                    "danger"
                )

                return redirect(
                    url_for(
                        "growth_stage.detail",
                        stage_id=growth_stage.id
                    )
                )

            flash(
                "Growth stage deleted successfully.",
                "success"
            )

            return redirect(
                url_for("growth_stage.index")
            )

        return render_template(
            "growth_stages/delete_confirm.html",
            growth_stage=growth_stage
        )

    except Exception:

        flash(
            "Unable to delete growth stage.",
            "danger"
        )

        return redirect(
            url_for("growth_stage.index")
        )