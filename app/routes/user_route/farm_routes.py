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

from app.services.farm_service import FarmService
from app.forms.farm_forms import (
    FarmCreateForm,
    FarmEditForm,
    FarmConfirmDeleteForm
)

farm_bp = Blueprint("farms",__name__,url_prefix="/user/farms",template_folder="../../templates")

# =========================================================
# FARM LIST
# =========================================================

@farm_bp.route("/")
@login_required
def index():

    farms = FarmService.get_all(
        user_id=current_user.id
    )

    return render_template(
        "user_page/farms/index.html",
        farms=farms
    )


# =========================================================
# FARM DETAIL
# =========================================================

@farm_bp.route("/<int:farm_id>")
@login_required
def detail(farm_id):

    farm = FarmService.get_by_id(
        farm_id,
        user_id=current_user.id
    )

    if not farm:
        abort(404)

    return render_template(
        "user_page/farms/detail.html",
        farm=farm
    )


# =========================================================
# CREATE FARM
# =========================================================

@farm_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():
    form = FarmCreateForm()
    if form.validate_on_submit():
        try:
            FarmService.create(
                user_id=current_user.id,
                farm_name=form.farm_name.data.strip(),
                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),
                location=(
                    form.location.data.strip()
                    if form.location.data
                    else None
                ),
                status=form.status.data
            )

            flash(
                "Farm created successfully.",
                "success"
            )

            return redirect(
                url_for("farms.index")
            )

        except (ValueError, TypeError):

            flash(
                "Invalid input data.",
                "danger"
            )

    return render_template(
        "user_page/farms/create.html",
        form=form,
        form_action=url_for("farms.create"),
        cancel_url=url_for("farms.index")
    )


# =========================================================
# EDIT FARM
# =========================================================

@farm_bp.route(
    "/<int:farm_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(farm_id):
    farm = FarmService.get_by_id(
        farm_id,
        user_id=current_user.id
    )
    if not farm:
        abort(404)
    form = FarmEditForm(obj=farm)
    if form.validate_on_submit():
        try:
            FarmService.update(
                farm=farm,
                farm_name=form.farm_name.data.strip(),
                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),
                location=(
                    form.location.data.strip()
                    if form.location.data
                    else None
                ),
                status=form.status.data
            )
            flash("Farm updated successfully.","success")
            return redirect(
                url_for("farms.detail",farm_id=farm.id)
            )
        except (ValueError, TypeError):
            flash("Invalid input data.","danger")
    return render_template(
        "user_page/farms/edit.html",
        form=form,
        farm=farm,
        form_action=url_for(
            "farms.edit",
            farm_id=farm.id
        ),
        cancel_url=url_for(
            "farms.detail",
            farm_id=farm.id
        )
    )


# =========================================================
# DELETE FARM CONFIRMATION
# =========================================================

@farm_bp.route("/<int:farm_id>/delete",methods=["GET", "POST"])
@login_required
def delete_confirm(farm_id):
    farm = FarmService.get_by_id(
        farm_id,
        user_id=current_user.id
    )

    if not farm:
        abort(404)

    form = FarmConfirmDeleteForm()
    if form.validate_on_submit():
        FarmService.delete(farm)
        flash(
            "Farm deleted successfully.",
            "success"
        )

        return redirect(
            url_for("farms.index")
        )

    return render_template(
        "user_page/farms/delete_confirm.html",
        farm=farm,
        form=form
    )