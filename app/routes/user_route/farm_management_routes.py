from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.decorators.access import role_required
from app.forms.farm_forms import FarmCreateForm
from app.forms.field_forms import FieldForm
from app.forms.field_crop_form import FieldCropForm
from app.models.farm import FarmTable
from app.models.field import FieldTable
from app.models.field_crop import FieldCropTable
from app.services.audit_service import log_audit
from app.services.farm_service import FarmService
from app.services.field_service import FieldService
from app.services.field_crop_service import FieldCropService
from app.services.growth_stage_service import GrowthStageService
from app.services.rice_variety_service import RiceVarietyService

farm_management_bp = Blueprint(
    "farm_management",
    __name__,
    url_prefix="/user/farm-management",
    template_folder="../../templates"
)

VIEW_PERMISSIONS = ("VIEW_FARM", "VIEW_FEILD", "VIEW_FIELD_CROP")


@farm_management_bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("User")
def index():
    if not all(current_user.has_permission(code) for code in VIEW_PERMISSIONS):
        flash("You do not have permission to view farm management.", "danger")
        return redirect(url_for("user.dashboard"))

    can_create_farm = current_user.has_permission("CREATE_FARM")
    can_create_field = current_user.has_permission("CREATE_FEILD")
    can_create_crop = current_user.has_permission("CREATE_FIELD_CROP")

    form_meta = {"csrf": False}
    farm_form = FarmCreateForm(prefix="farm", meta=form_meta)
    field_form = FieldForm(prefix="field", meta=form_meta)
    crop_form = FieldCropForm(prefix="crop", meta=form_meta)

    farms = FarmService.get_all(user_id=current_user.id)
    fields = FieldService.get_all(user_id=current_user.id)
    can_start_workflow = can_create_crop and (
        bool(fields)
        or (bool(farms) and can_create_field)
        or (can_create_farm and can_create_field)
    )
    rice_varieties = RiceVarietyService.get_active()
    growth_stages = GrowthStageService.get_active()

    crop_form.field_id.choices = [(field.id, field.field_name) for field in fields]
    crop_form.rice_variety_id.choices = [
        (
            variety.id,
            f"{variety.variety_name} - {variety.name_kh}"
            if variety.name_kh
            else variety.variety_name
        )
        for variety in rice_varieties
    ]
    crop_form.growth_stage_id.choices = [
        (stage.id, f"{stage.stage_name} / {stage.stage_name_kh}")
        for stage in growth_stages
    ]

    selected_farm_id = request.form.get(
        "farm_id",
        str(farms[0].id) if farms else (
            "new" if can_create_farm and can_create_field else ""
        )
    )
    selected_field_mode = request.form.get(
        "field_mode",
        "existing" if fields else "new"
    )
    selected_existing_field_id = request.form.get("existing_field_id", "")
    if not selected_existing_field_id:
        selected_existing_field_id = next(
            (
                str(field.id)
                for field in fields
                if str(field.farm_id) == str(selected_farm_id)
            ),
            ""
        )

    def render_page(errors=None, open_create_form=False):
        crops = FieldCropService.get_all(user_id=current_user.id)
        return render_template(
            "user_page/farm_management/index.html",
            farms=farms,
            fields=fields,
            crops=crops,
            farm_form=farm_form,
            field_form=field_form,
            crop_form=crop_form,
            rice_varieties=rice_varieties,
            management_errors=errors or [],
            selected_farm_id=str(selected_farm_id),
            selected_field_mode=selected_field_mode,
            selected_existing_field_id=str(selected_existing_field_id),
            can_create_farm=can_create_farm,
            can_create_field=can_create_field,
            can_create_crop=can_create_crop,
            can_create_farm_and_field=can_create_farm and can_create_field,
            can_start_workflow=can_start_workflow,
            open_create_form=open_create_form
        )

    if request.method == "GET":
        return render_page()

    errors = []
    if not can_create_crop:
        errors.append("You do not have permission to add a field crop.")
    if not rice_varieties:
        errors.append("Add an active rice variety before creating a field crop.")

    farm = None
    creating_farm = selected_farm_id == "new"
    if creating_farm:
        if not can_create_farm:
            errors.append("You do not have permission to create a farm.")
        if not can_create_field:
            errors.append("A new farm requires permission to create its field.")
        if not farm_form.validate():
            errors.append("Please correct the farm information.")
    else:
        try:
            farm_id = int(selected_farm_id)
        except (TypeError, ValueError):
            farm_id = None
        farm = FarmService.get_by_id(farm_id, user_id=current_user.id) if farm_id else None
        if farm is None:
            errors.append("Select a valid farm belonging to your account.")

    creating_field = creating_farm or selected_field_mode == "new"
    field = None
    if creating_farm and selected_field_mode != "new":
        errors.append("A new farm must have a new field.")
    elif creating_field:
        if not can_create_field:
            errors.append("You do not have permission to create a field.")
        if not field_form.validate():
            errors.append("Please correct the field information.")
    elif farm is not None:
        try:
            field_id = int(selected_existing_field_id)
        except (TypeError, ValueError):
            field_id = None
        field = FieldService.get_by_id(field_id, user_id=current_user.id) if field_id else None
        if field is None or field.farm_id != farm.id:
            errors.append("Select a field that belongs to the selected farm.")
    else:
        errors.append("Select a valid field.")

    if errors:
        return render_page(errors, open_create_form=True)

    try:
        if creating_farm:
            farm = FarmTable(
                user_id=current_user.id,
                farm_name=farm_form.farm_name.data.strip(),
                province=farm_form.province.data,
                district=farm_form.district.data.strip(),
                commune=farm_form.commune.data.strip(),
                description=(farm_form.description.data or "").strip() or None,
                location=(farm_form.location.data or "").strip() or None,
                status=farm_form.status.data
            )
            db.session.add(farm)
            db.session.flush()

        if creating_field:
            field = FieldTable(
                farm_id=farm.id,
                field_name=field_form.field_name.data.strip(),
                area=field_form.area.data,
                soil_type=field_form.soil_type.data or None,
                location=(field_form.location.data or "").strip() or None,
                boundary=field_form.boundary.data or None,
                description=(field_form.description.data or "").strip() or None,
                status=field_form.status.data
            )
            db.session.add(field)
            db.session.flush()

        crop_form.field_id.choices = [(field.id, field.field_name)]
        crop_form.field_id.data = field.id
        if not crop_form.validate():
            db.session.rollback()
            return render_page(["Please correct the field crop information."], open_create_form=True)

        crop = FieldCropTable(
            field_id=field.id,
            rice_variety_id=crop_form.rice_variety_id.data,
            growth_stage_id=crop_form.growth_stage_id.data or None,
            planting_date=crop_form.planting_date.data,
            expected_harvest_date=crop_form.expected_harvest_date.data,
            actual_harvest_date=crop_form.actual_harvest_date.data,
            area=crop_form.area.data,
            season=crop_form.season.data or None,
            year=crop_form.year.data,
            status=crop_form.status.data,
            description=(crop_form.description.data or "").strip() or None
        )
        db.session.add(crop)
        db.session.commit()

        if creating_farm:
            log_audit(
                action="CREATE",
                table_name="farms",
                record_id=farm.id,
                after_data={
                    "user_id": current_user.id,
                    "farm_name": farm.farm_name,
                    "province": farm.province,
                    "district": farm.district,
                    "commune": farm.commune,
                    "description": farm.description,
                    "location": farm.location,
                    "status": farm.status
                }
            )
        if creating_field:
            log_audit(
                action="CREATE",
                table_name="fields",
                record_id=field.id,
                after_data={
                    "farm_id": farm.id,
                    "field_name": field.field_name,
                    "area": field.area,
                    "soil_type": field.soil_type,
                    "location": field.location,
                    "boundary": field.boundary,
                    "description": field.description,
                    "status": field.status
                }
            )
        log_audit(
            action="CREATE",
            table_name="field_crops",
            record_id=crop.id,
            after_data={
                "field_id": field.id,
                "rice_variety_id": crop.rice_variety_id,
                "growth_stage_id": crop.growth_stage_id,
                "planting_date": crop.planting_date,
                "expected_harvest_date": crop.expected_harvest_date,
                "actual_harvest_date": crop.actual_harvest_date,
                "area": crop.area,
                "season": crop.season,
                "year": crop.year,
                "status": crop.status,
                "description": crop.description
            }
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Combined farm, field, and crop creation failed")
        flash("Unable to save the farm, field, and crop. Please try again.", "danger")
        return render_page(open_create_form=True)

    flash("Farm, field, and field crop saved successfully.", "success")
    return redirect(url_for("farm_management.index"))
