from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from extensions import db

from app.forms.field_forms import FieldForm, FieldConfirmDeleteForm
from app.services.field_service import FieldService
from app.services.farm_service import FarmService

from app.decorators.access import role_required, permission_required
# =========================================================
# BLUEPRINT
# =========================================================
# user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="../../templates")

field_bp = Blueprint("fields",__name__,url_prefix="/user/fields", template_folder="../../templates")

# =========================================================
# FIELD LIST
# =========================================================

@field_bp.route("/")
@login_required
@role_required("User")
@permission_required("VIEW_FEILD")
def index():

    try:

        fields = FieldService.get_all(
            user_id=current_user.id
        )

        return render_template(
            "user_page/fields/index.html",
            fields=fields
        )

    except Exception as e:

        print(
            f"Field index error: {e}"
        )

        flash(
            "Unable to load fields.",
            "danger"
        )

        return render_template(
            "user_page/fields/index.html",
            fields=[]
        )


# =========================================================
# FIELD DETAIL
# =========================================================

@field_bp.route("/<int:field_id>")
@login_required
@role_required("User")
@permission_required("DETAIL_FEILD")
def detail(field_id):

    try:

        field = FieldService.get_by_id(
            field_id=field_id,
            user_id=current_user.id
        )

        if not field:
            abort(404)

        return render_template(
            "user_page/fields/detail.html",
            field=field
        )

    except Exception as e:

        print(
            f"Field detail error: {e}"
        )

        flash(
            "Unable to load field.",
            "danger"
        )

        return redirect(
            url_for("fields.index")
        )


# =========================================================
# CREATE FIELD
# =========================================================

@field_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
@role_required("User")
@permission_required("CREATE_FEILD")
def create():

    form = FieldForm()

    try:

        # -------------------------------------------------
        # Get current user's farms
        # -------------------------------------------------

        farms = FarmService.get_all(
            user_id=current_user.id
        )


        # -------------------------------------------------
        # No farm
        # -------------------------------------------------

        if not farms:

            flash(
                "Please create a farm before creating a field.",
                "warning"
            )

            return redirect(
                url_for("farms.create")
            )


        # -------------------------------------------------
        # POST
        # -------------------------------------------------

        if form.validate_on_submit():

            # Get farm_id from HTML select

            farm_id = request.form.get(
                "farm_id",
                type=int
            )


            # -------------------------------------------------
            # Validate farm selection
            # -------------------------------------------------

            if not farm_id:

                flash(
                    "Please select a farm.",
                    "danger"
                )

                return render_template(
                    "user_page/fields/create.html",

                    form=form,

                    farms=farms,

                    form_action=url_for(
                        "fields.create"
                    ),

                    cancel_url=url_for(
                        "fields.index"
                    )
                )


            # -------------------------------------------------
            # Check farm belongs to current user
            # -------------------------------------------------

            farm = FarmService.get_by_id(
                farm_id=farm_id,
                user_id=current_user.id
            )


            if not farm:

                flash(
                    "Invalid farm selected.",
                    "danger"
                )

                return render_template(
                    "user_page/fields/create.html",

                    form=form,

                    farms=farms,

                    form_action=url_for(
                        "fields.create"
                    ),

                    cancel_url=url_for(
                        "fields.index"
                    )
                )


            # -------------------------------------------------
            # Create field
            # -------------------------------------------------

            FieldService.create(

                farm_id=farm.id,

                field_name=form.field_name.data.strip(),

                area=form.area.data,

                soil_type=(
                    form.soil_type.data.strip()
                    if form.soil_type.data
                    else None
                ),

                location=(
                    form.location.data.strip()
                    if form.location.data
                    else None
                ),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),

                status=form.status.data
            )


            # -------------------------------------------------
            # Success
            # -------------------------------------------------

            flash(
                "Field created successfully.",
                "success"
            )

            return redirect(
                url_for("fields.index")
            )


        # -------------------------------------------------
        # GET / Validation Failed
        # -------------------------------------------------

        return render_template(

            "user_page/fields/create.html",

            form=form,

            farms=farms,

            form_action=url_for(
                "fields.create"
            ),

            cancel_url=url_for(
                "fields.index"
            )
        )


    except Exception as e:

        db.session.rollback()

        print(
            f"Field create error: {e}"
        )

        flash(
            "An error occurred while creating the field.",
            "danger"
        )


        # Reload farms

        try:

            farms = FarmService.get_all(
                user_id=current_user.id
            )

        except Exception:

            farms = []


        return render_template(

            "user_page/fields/create.html",

            form=form,

            farms=farms,

            form_action=url_for(
                "fields.create"
            ),

            cancel_url=url_for(
                "fields.index"
            )
        )


# =========================================================
# EDIT FIELD
# =========================================================

@field_bp.route(
    "/<int:field_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("User")
@permission_required("EDIT_FEILD")
def edit(field_id):
    try:
        # -------------------------------------------------
        # Get field
        # -------------------------------------------------
        field = FieldService.get_by_id(
            field_id=field_id,
            user_id=current_user.id
        )


        if not field:
            abort(404)


        # -------------------------------------------------
        # Get farms
        # -------------------------------------------------

        farms = FarmService.get_all(
            user_id=current_user.id
        )


        # -------------------------------------------------
        # Form
        # -------------------------------------------------

        form = FieldForm(
            obj=field
        )


        # -------------------------------------------------
        # POST
        # -------------------------------------------------

        if form.validate_on_submit():

            farm_id = request.form.get(
                "farm_id",
                type=int
            )


            # -------------------------------------------------
            # Validate farm
            # -------------------------------------------------

            if not farm_id:

                flash(
                    "Please select a farm.",
                    "danger"
                )

                return render_template(
                    "user_page/fields/edit.html",

                    form=form,

                    field=field,

                    farms=farms,

                    form_action=url_for(
                        "fields.edit",
                        field_id=field.id
                    ),

                    cancel_url=url_for(
                        "fields.detail",
                        field_id=field.id
                    )
                )


            # -------------------------------------------------
            # Check farm belongs to current user
            # -------------------------------------------------

            farm = FarmService.get_by_id(
                farm_id=farm_id,
                user_id=current_user.id
            )


            if not farm:

                flash(
                    "Invalid farm selected.",
                    "danger"
                )

                return render_template(
                    "user_page/fields/edit.html",

                    form=form,

                    field=field,

                    farms=farms,

                    form_action=url_for(
                        "fields.edit",
                        field_id=field.id
                    ),

                    cancel_url=url_for(
                        "fields.detail",
                        field_id=field.id
                    )
                )


            # -------------------------------------------------
            # Update field
            # -------------------------------------------------

            field.farm_id = farm.id


            FieldService.update(

                field=field,

                field_name=form.field_name.data.strip(),

                area=form.area.data,

                soil_type=(
                    form.soil_type.data.strip()
                    if form.soil_type.data
                    else None
                ),

                location=(
                    form.location.data.strip()
                    if form.location.data
                    else None
                ),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),

                status=form.status.data
            )


            flash(
                "Field updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "fields.detail",
                    field_id=field.id
                )
            )


        # -------------------------------------------------
        # GET
        # -------------------------------------------------

        return render_template(

            "user_page/fields/edit.html",

            form=form,

            field=field,

            farms=farms,

            form_action=url_for(
                "fields.edit",
                field_id=field.id
            ),

            cancel_url=url_for(
                "fields.detail",
                field_id=field.id
            )
        )


    except Exception as e:

        db.session.rollback()

        print(
            f"Field edit error: {e}"
        )

        flash(
            "An error occurred while updating the field.",
            "danger"
        )

        return redirect(
            url_for("fields.index")
        )


# =========================================================
# DELETE FIELD
# # =========================================================
# @field_bp.route("/<int:field_id>/delete",methods=["POST"])
# @login_required
# def delete(field_id):

#     try:
#         # -------------------------------------------------
#         # Get field
#         # -------------------------------------------------

#         field = FieldService.get_by_id(
#             field_id=field_id,
#             user_id=current_user.id
#         )
#         if not field:
#             abort(404)
#         # -------------------------------------------------
#         # Delete
#         # -------------------------------------------------
#         FieldService.delete(field)
#         flash("Field deleted successfully.","success")
#         return redirect(url_for("fields.index"))
    
#     except Exception as e:
#         db.session.rollback()
#         print(f"Field delete error: {e}")
#         flash("An error occurred while deleting the field.","danger")
#         return redirect(url_for("fields.index"))

@field_bp.route("/<int:field_id>/delete",methods=["GET", "POST"])
@login_required
@role_required("User")
@permission_required("DELETE_FEILD")
def delete_confirm(field_id):
    field = FieldService.get_by_id(
        field_id,
        user_id=current_user.id
    )

    if not field:
        abort(404)

    form = FieldConfirmDeleteForm()
    if form.validate_on_submit():
        FieldService.delete(field)
        flash(
            "Farm deleted successfully.",
            "success"
        )

        return redirect(
            url_for("fields.index")
        )

    return render_template(
        "user_page/fields/delete_confirm.html",
        field=field,
        form=form
    )