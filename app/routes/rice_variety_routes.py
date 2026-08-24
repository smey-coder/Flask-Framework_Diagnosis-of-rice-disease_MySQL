from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request
)

from flask_login import login_required

from app.services.rice_variety_service import (
    RiceVarietyService
)

from app.forms.rice_variety_forms import RiceVarietyForm, DeleteConfirmForm

from app.decorators.access import role_required, permission_required


# =========================================================
# BLUEPRINT
# =========================================================

rice_variety_bp = Blueprint(
    "rice_variety",
    __name__,
    url_prefix="/rice-varieties"
)


# =========================================================
# INDEX
# =========================================================

@rice_variety_bp.route("/")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_RICE_VARIETY")
def index():
    try:
        varieties = RiceVarietyService.get_all()

        return render_template(
            "rice_variets/index.html",
            varieties=varieties
        )

    except Exception as e:

        print(
            f"RiceVariety index error: {e}"
        )

        flash(
            "Unable to load rice varieties.",
            "danger"
        )

        return render_template(
            "rice_variets/index.html",
            varieties=[]
        )


# =========================================================
# CREATE
# =========================================================

@rice_variety_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_RICE_VARIETY")
def create():
    form = RiceVarietyForm()
    try:
        if form.validate_on_submit():
            success, result = RiceVarietyService.create(
                variety_name=(
                    form.variety_name.data.strip()
                ),
                name_kh=(
                    form.name_kh.data.strip()
                ),

                growth_duration_days=(
                    form.growth_duration_days.data
                ),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),

                status=form.status.data
            )

            if not success:

                flash(
                    result,
                    "danger"
                )

                return render_template(
                    "rice_variets/create.html",
                    form=form
                )

            flash(
                "Rice variety created successfully.",
                "success"
            )

            return redirect(url_for("rice_variety.index"))

        return render_template(
            "rice_variets/create.html",
            form=form
        )

    except Exception as e:

        print(
            f"RiceVariety create route error: {e}"
        )

        flash(
            "Unable to create rice variety.",
            "danger"
        )

        return render_template(
            "rice_variets/create.html",
            form=form
        )


# =========================================================
# DETAIL
# =========================================================

@rice_variety_bp.route(
    "/<int:variety_id>"
)
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_RICE_VARIETY")
def detail(variety_id):

    try:

        variety = RiceVarietyService.get_by_id(
            variety_id
        )

        if not variety:

            abort(404)

        return render_template(
            "rice_variets/detail.html",
            variety=variety
        )

    except Exception as e:

        print(
            f"RiceVariety detail route error: {e}"
        )

        flash(
            "Unable to load rice variety.",
            "danger"
        )

        return redirect(
            url_for(
                "rice_variety.index"
            )
        )


# =========================================================
# EDIT
# =========================================================

@rice_variety_bp.route(
    "/<int:variety_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin", "Expert")
@permission_required("UPDATE_RICE_VARIETY")
def edit(variety_id):

    form = RiceVarietyForm()

    try:

        variety = RiceVarietyService.get_by_id(
            variety_id
        )

        if not variety:

            abort(404)

        # -------------------------------------------------
        # LOAD EXISTING DATA
        # -------------------------------------------------

        if request.method == "GET":

            form = RiceVarietyForm(
                obj=variety
            )

        # -------------------------------------------------
        # SUBMIT
        # -------------------------------------------------

        if form.validate_on_submit():

            success, error = (
                RiceVarietyService.update(

                    variety=variety,

                    variety_name=(
                        form.variety_name.data.strip()
                    ),

                    name_kh=(
                        form.name_kh.data.strip()
                    ),

                    growth_duration_days=(
                        form.growth_duration_days.data
                    ),

                    description=(
                        form.description.data.strip()
                        if form.description.data
                        else None
                    ),

                    status=form.status.data
                )
            )

            if not success:

                flash(
                    error,
                    "danger"
                )

                return render_template(
                    "rice_variets/edit.html",
                    form=form,
                    variety=variety
                )

            flash(
                "Rice variety updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "rice_variety.detail",
                    variety_id=variety.id
                )
            )

        return render_template(
            "rice_variets/edit.html",
            form=form,
            variety=variety
        )

    except Exception as e:

        print(
            f"RiceVariety edit route error: {e}"
        )

        flash(
            "Unable to update rice variety.",
            "danger"
        )

        return redirect(
            url_for(
                "rice_variety.index"
            )
        )


# =========================================================
# DELETE CONFIRM
# =========================================================

@rice_variety_bp.route(
    "/<int:variety_id>/delete",
    methods=["GET", "POST"]
)
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_RICE_VARIETY")
def delete_confirm(variety_id):

    delete_form = DeleteConfirmForm()

    try:

        # -------------------------------------------------
        # GET VARIETY
        # -------------------------------------------------

        variety = RiceVarietyService.get_by_id(
            variety_id
        )

        if not variety:
            abort(404)

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        if delete_form.validate_on_submit():

            success, error = RiceVarietyService.delete(
                variety
            )

            if not success:

                flash(
                    error,
                    "danger"
                )

                return redirect(
                    url_for(
                        "rice_variety.detail",
                        variety_id=variety.id
                    )
                )

            flash(
                "Rice variety deleted successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "rice_variety.index"
                )
            )

        # -------------------------------------------------
        # GET / VALIDATION ERROR
        # -------------------------------------------------

        return render_template(
            "rice_variets/delete_confirm.html",
            variety=variety,
            delete_form=delete_form
        )

    except Exception as e:

        print(
            f"RiceVariety delete route error: {e}"
        )

        flash(
            "Unable to delete rice variety.",
            "danger"
        )

        return redirect(
            url_for(
                "rice_variety.index"
            )
        )