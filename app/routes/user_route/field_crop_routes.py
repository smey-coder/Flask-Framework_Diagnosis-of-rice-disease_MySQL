from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db

from app.services.field_service import FieldService

from app.forms.field_crop_form import (
    FieldCropForm,
    FieldCropDeleteForm
)

from app.services.field_crop_service import (
    FieldCropService
)

from app.services.field_service import (
    FieldService
)

from app.services.rice_variety_service import (
    RiceVarietyService
)

from app.services.growth_stage_service import (
    GrowthStageService
)


field_crop_bp = Blueprint("field_crops",__name__,url_prefix="/user/field-crops", template_folder="../../templates")
# =========================================================
# INDEX
# =========================================================

@field_crop_bp.route("/")
@login_required
def index():

    try:

        crops = FieldCropService.get_all(
            user_id=current_user.id
        )

        return render_template(
            "user_page/field_crops/index.html",
            crops=crops
        )

    except Exception as e:

        print(
            f"Field crop index error: {e}"
        )

        flash(
            "Unable to load field crops.",
            "danger"
        )

        return render_template(
            "user_page/field_crops/index.html",
            crops=[]
        )


# =========================================================
# DETAIL
# =========================================================

@field_crop_bp.route(
    "/<int:crop_id>"
)
@login_required
def detail(crop_id):

    try:

        crop = FieldCropService.get_by_id(
            crop_id=crop_id,
            user_id=current_user.id
        )

        if not crop:

            abort(404)

        return render_template(
            "user_page/field_crops/detail.html",
            crop=crop
        )

    except Exception as e:

        print(
            f"Field crop detail error: {e}"
        )

        flash(
            "Unable to load field crop.",
            "danger"
        )

        return redirect(
            url_for(
                "field_crops.index"
            )
        )


# =========================================================
# CREATE
# =========================================================

@field_crop_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    form = FieldCropForm()

    fields = []
    rice_varieties = []
    growth_stages = []

    try:

        # =====================================================
        # LOAD DATA
        # =====================================================

        fields = FieldService.get_all(
            user_id=current_user.id
        )

        rice_varieties = RiceVarietyService.get_active()

        growth_stages = GrowthStageService.get_active()

        # =====================================================
        # SET FIELD CHOICES
        # =====================================================

        form.field_id.choices = [
            (
                field.id,
                field.field_name
            )
            for field in fields
        ]

        # =====================================================
        # SET RICE VARIETY CHOICES
        # =====================================================

        form.rice_variety_id.choices = [
            (
                variety.id,
                (
                    f"{variety.variety_name} - "
                    f"{variety.name_kh}"
                    if variety.name_kh
                    else variety.variety_name
                )
            )
            for variety in rice_varieties
        ]

        # =====================================================
        # SET GROWTH STAGE CHOICES
        # =====================================================

        form.growth_stage_id.choices = [
            (
                stage.id,
                f"{stage.stage_name} / {stage.stage_name_kh}"
            )
            for stage in growth_stages
        ]

        # =====================================================
        # CHECK FIELD
        # =====================================================

        if not fields:

            flash(
                "Please create a field before creating a field crop.",
                "warning"
            )

            return redirect(
                url_for("fields.create")
            )

        # =====================================================
        # CHECK RICE VARIETY
        # =====================================================

        if not rice_varieties:

            flash(
                "Please create a rice variety first.",
                "warning"
            )

            return redirect(
                url_for("rice_varieties.create")
            )

        # =====================================================
        # POST
        # =====================================================

        if form.validate_on_submit():

            FieldCropService.create(

                field_id=form.field_id.data,

                rice_variety_id=form.rice_variety_id.data,

                growth_stage_id=(
                    form.growth_stage_id.data
                    if form.growth_stage_id.data
                    else None
                ),

                planting_date=form.planting_date.data,

                expected_harvest_date=(
                    form.expected_harvest_date.data
                ),

                actual_harvest_date=(
                    form.actual_harvest_date.data
                ),

                area=form.area.data,

                status=form.status.data,

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                )
            )

            flash(
                "Field crop created successfully.",
                "success"
            )

            return redirect(
                url_for("field_crops.index")
            )

        # =====================================================
        # RENDER
        # =====================================================

        return render_template(

            "user_page/field_crops/create.html",

            form=form,

            fields=fields,

            rice_varieties=rice_varieties,

            growth_stages=growth_stages,

            form_action=url_for(
                "field_crops.create"
            ),

            cancel_url=url_for(
                "field_crops.index"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"FieldCrop create error: {e}"
        )

        flash(
            "An error occurred while creating field crop.",
            "danger"
        )

        return render_template(

            "user_page/field_crops/create.html",

            form=form,

            fields=fields,

            rice_varieties=rice_varieties,

            growth_stages=growth_stages,

            form_action=url_for(
                "field_crops.create"
            ),

            cancel_url=url_for(
                "field_crops.index"
            )
        )


# =========================================================
# EDIT
# =========================================================

@field_crop_bp.route(
    "/<int:crop_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(crop_id):

    try:

        crop = FieldCropService.get_by_id(
            crop_id=crop_id,
            user_id=current_user.id
        )

        if not crop:

            abort(404)

        fields = FieldService.get_all(
            user_id=current_user.id
        )

        varieties = RiceVarietyService.get_all()

        growth_stages = GrowthStageService.get_all()

        form = FieldCropForm(
            obj=crop
        )

        form.field_id.choices = [

            (
                field.id,
                field.field_name
            )

            for field in fields

        ]

        form.rice_variety_id.choices = [

            (
                variety.id,
                variety.variety_name
            )

            for variety in varieties

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

        if not form.is_submitted():

            form.field_id.data = crop.field_id

            form.rice_variety_id.data = (
                crop.rice_variety_id
            )

            form.growth_stage_id.data = (
                crop.growth_stage_id
                if crop.growth_stage_id
                else 0
            )

        if form.validate_on_submit():

            growth_stage_id = (
                form.growth_stage_id.data
                if form.growth_stage_id.data != 0
                else None
            )

            FieldCropService.update(

                crop=crop,

                rice_variety_id=(
                    form.rice_variety_id.data
                ),

                growth_stage_id=growth_stage_id,

                planting_date=(
                    form.planting_date.data
                ),

                expected_harvest_date=(
                    form.expected_harvest_date.data
                ),

                actual_harvest_date=(
                    form.actual_harvest_date.data
                ),

                area=form.area.data,

                status=form.status.data,

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                )
            )

            flash(
                "Field crop updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "field_crops.detail",
                    crop_id=crop.id
                )
            )

        return render_template(
            "user_page/field_crops/edit.html",
            form=form,
            crop=crop,
            fields=fields,
            varieties=varieties,
            growth_stages=growth_stages,
            form_action=url_for(
                "field_crops.edit",
                crop_id=crop.id
            ),
            cancel_url=url_for(
                "field_crops.detail",
                crop_id=crop.id
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Field crop edit error: {e}"
        )

        flash(
            "An error occurred while updating the field crop.",
            "danger"
        )

        return redirect(
            url_for(
                "field_crops.index"
            )
        )


# =========================================================
# DELETE CONFIRM
# =========================================================

@field_crop_bp.route(
    "/<int:crop_id>/delete",
    methods=["GET", "POST"]
)
@login_required
def delete_confirm(crop_id):

    try:

        crop = FieldCropService.get_by_id(
            crop_id=crop_id,
            user_id=current_user.id
        )

        if not crop:

            abort(404)

        form = FieldCropDeleteForm()

        if form.validate_on_submit():

            FieldCropService.delete(
                crop
            )

            flash(
                "Field crop deleted successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "field_crops.index"
                )
            )

        return render_template(
            "user_page/field_crops/delete_confirm.html",
            crop=crop,
            form=form,
            cancel_url=url_for(
                "field_crops.detail",
                crop_id=crop.id
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Field crop delete error: {e}"
        )

        flash(
            "An error occurred while deleting the field crop.",
            "danger"
        )

        return redirect(
            url_for(
                "field_crops.index"
            )
        )