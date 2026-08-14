from datetime import date

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from app.decorators.access import role_required
from extensions import db

from app.forms.crop_monitoring_form import (
    CropMonitoringForm,
    CropMonitoringDeleteForm
)

from app.services.crop_monitoring_service import (
    CropMonitoringService
)

from app.services.field_crop_service import (
    FieldCropService
)

from app.services.growth_stage_service import (
    GrowthStageService
)


crop_monitoring_bp = Blueprint("crop_monitoring",__name__,url_prefix="/user/crop-monitoring",template_folder="../../templates")


# =========================================================
# CROP MONITORING
# =========================================================

@crop_monitoring_bp.route("/crop-monitoring",methods=["GET"])
@login_required
def index():

    try:

        monitorings = CropMonitoringService.get_all(
            user_id=current_user.id
        )

        return render_template(
            "user_page/crop_monitorings/index.html",
            monitorings=monitorings
        )

    except Exception as e:

        print(
            f"Crop Monitoring index error: {e}"
        )

        flash(
            "An error occurred while loading crop monitoring.",
            "danger"
        )

        return redirect(
            url_for("user.dashboard")
        )


# =========================================================
# CREATE
# =========================================================

@crop_monitoring_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    form = CropMonitoringForm()

    try:

        # -------------------------------------------------
        # Load Field Crops
        # -------------------------------------------------

        field_crops = FieldCropService.get_all(
            user_id=current_user.id
        )

        # -------------------------------------------------
        # Load Growth Stages
        # -------------------------------------------------

        growth_stages = GrowthStageService.get_active()

        # -------------------------------------------------
        # FIELD CROP CHOICES
        # -------------------------------------------------

        form.field_crop_id.choices = [
            (
                crop.id,
                f"{crop.field.field_name} - "
                f"{crop.rice_variety.variety_name}"
            )
            for crop in field_crops
        ]

        # -------------------------------------------------
        # GROWTH STAGE CHOICES
        # -------------------------------------------------

        form.growth_stage_id.choices = [
            (
                0,
                "-- Select Growth Stage --"
            )
        ] + [
            (
                stage.id,
                stage.stage_name
            )
            for stage in growth_stages
        ]

        # -------------------------------------------------
        # POST
        # -------------------------------------------------

        if form.validate_on_submit():

            growth_stage_id = (
                form.growth_stage_id.data
                if form.growth_stage_id.data != 0
                else None
            )

            CropMonitoringService.create(

                field_crop_id=(
                    form.field_crop_id.data
                ),

                monitoring_date=(
                    form.monitoring_date.data
                ),

                growth_stage_id=(
                    growth_stage_id
                ),

                plant_height=(
                    form.plant_height.data
                ),

                water_status=(
                    form.water_status.data
                    or None
                ),

                plant_condition=(
                    form.plant_condition.data
                    or None
                ),

                pest_status=(
                    form.pest_status.data
                    or None
                ),

                disease_status=(
                    form.disease_status.data
                    or None
                ),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                )
            )

            flash(
                "Crop monitoring created successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "crop_monitoring.index"
                )
            )

        # -------------------------------------------------
        # GET / Validation Failed
        # -------------------------------------------------

        return render_template(
            "user_page/crop_monitorings/create.html",
            form=form,
            field_crops=field_crops,
            growth_stages=growth_stages,
            form_action=url_for(
                "crop_monitoring.create"
            ),
            cancel_url=url_for(
                "crop_monitoring.index"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Crop Monitoring create error: {e}"
        )

        flash(
            "An error occurred while creating crop monitoring.",
            "danger"
        )

        return render_template(
            "user_page/crop_monitorings/create.html",
            form=form,
            field_crops=[],
            growth_stages=[],
            form_action=url_for(
                "crop_monitoring.create"
            ),
            cancel_url=url_for(
                "crop_monitoring.index"
            )
        )


# =========================================================
# EDIT
# =========================================================

@crop_monitoring_bp.route(
    "/<int:monitoring_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(
    monitoring_id
):

    form = CropMonitoringForm()

    try:

        # -------------------------------------------------
        # Get Monitoring
        # -------------------------------------------------

        monitoring = CropMonitoringService.get_by_id(
            monitoring_id=monitoring_id,
            user_id=current_user.id
        )

        if not monitoring:

            abort(404)

        # -------------------------------------------------
        # Load Field Crops
        # -------------------------------------------------

        field_crops = FieldCropService.get_all(
            user_id=current_user.id
        )

        # -------------------------------------------------
        # Load Growth Stages
        # -------------------------------------------------

        growth_stages = GrowthStageService.get_active()

        # -------------------------------------------------
        # Choices
        # -------------------------------------------------

        form.field_crop_id.choices = [
            (
                crop.id,
                f"{crop.field.field_name} - "
                f"{crop.rice_variety.variety_name}"
            )
            for crop in field_crops
        ]

        form.growth_stage_id.choices = [
            (
                0,
                "-- Select Growth Stage --"
            )
        ] + [
            (
                stage.id,
                stage.stage_name
            )
            for stage in growth_stages
        ]

        # -------------------------------------------------
        # POST
        # -------------------------------------------------

        if form.validate_on_submit():

            growth_stage_id = (
                form.growth_stage_id.data
                if form.growth_stage_id.data != 0
                else None
            )

            CropMonitoringService.update(

                monitoring=monitoring,

                monitoring_date=(
                    form.monitoring_date.data
                ),

                growth_stage_id=(
                    growth_stage_id
                ),

                plant_height=(
                    form.plant_height.data
                ),

                water_status=(
                    form.water_status.data
                    or None
                ),

                plant_condition=(
                    form.plant_condition.data
                    or None
                ),

                pest_status=(
                    form.pest_status.data
                    or None
                ),

                disease_status=(
                    form.disease_status.data
                    or None
                ),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                )
            )

            flash(
                "Crop monitoring updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "crop_monitoring.index"
                )
            )

        # -------------------------------------------------
        # GET
        # -------------------------------------------------

        if not form.is_submitted():

            form.field_crop_id.data = (
                monitoring.field_crop_id
            )

            form.monitoring_date.data = (
                monitoring.monitoring_date
            )

            form.growth_stage_id.data = (
                monitoring.growth_stage_id or 0
            )

            form.plant_height.data = (
                monitoring.plant_height
            )

            form.water_status.data = (
                monitoring.water_status or ""
            )

            form.plant_condition.data = (
                monitoring.plant_condition or ""
            )

            form.pest_status.data = (
                monitoring.pest_status or ""
            )

            form.disease_status.data = (
                monitoring.disease_status or ""
            )

            form.description.data = (
                monitoring.description or ""
            )

        return render_template(
            "user_page/crop_monitorings/edit.html",
            form=form,
            monitoring=monitoring,
            field_crops=field_crops,
            growth_stages=growth_stages,
            form_action=url_for(
                "crop_monitoring.edit",
                monitoring_id=monitoring.id
            ),
            cancel_url=url_for(
                "crop_monitoring.index"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Crop Monitoring edit error: {e}"
        )

        flash(
            "An error occurred while updating crop monitoring.",
            "danger"
        )

        return redirect(
            url_for(
                "crop_monitoring.index"
            )
        )


# =========================================================
# DELETE
# =========================================================

@crop_monitoring_bp.route(
    "/<int:monitoring_id>/delete",
    methods=["GET", "POST"]
)
@login_required
@role_required("User")
def delete(monitoring_id):

    monitoring = CropMonitoringService.get_by_id(
        monitoring_id,
        current_user.id
    )

    if not monitoring:
        abort(404)

    form = CropMonitoringDeleteForm()

    if form.validate_on_submit():

        try:

            CropMonitoringService.delete(
                monitoring
            )

            flash(
                "Crop monitoring deleted successfully.",
                "success"
            )

            return redirect(
                url_for("crop_monitoring.index")
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"Crop monitoring delete error: {e}"
            )

            flash(
                "An error occurred while deleting crop monitoring.",
                "danger"
            )

            return redirect(
                url_for("crop_monitoring.index")
            )

    return render_template(
        "user_page/crop_monitorings/delete.html",
        monitoring=monitoring,
        form=form,
        cancel_url=url_for(
            "crop_monitoring.index"
        )
    )