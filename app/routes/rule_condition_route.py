from flask import (
    Blueprint, abort, render_template,
    redirect, url_for, flash, request
)
from flask_login import login_required

from app.forms.rule_condition_form import (
    RuleConditionCreateForm,
    RuleConditionEditForm,
    RuleConditionConfirmDeleteForm
)
from app.services.rule_condition_service import RuleConditionService

rule_condition_bp = Blueprint(
    "rule_condition",
    __name__,
    url_prefix="/admin/rule-conditions"
)

# ===================== INDEX =====================

@rule_condition_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    active_only = request.args.get("active", type=int)

    pagination = RuleConditionService.paginate(page=page)
    rule_conditions = pagination.items

    return render_template(
        "rule_condition_page/index.html",
        rule_conditions=rule_conditions,
        pagination=pagination,
        active_only=active_only
    )

# ===================== CREATE =====================

@rule_condition_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = RuleConditionCreateForm()

    if form.validate_on_submit():
        try:
            RuleConditionService.create(form.data)
            flash("Rule condition created successfully.", "success")
            return redirect(url_for("rule_condition.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template(
        "rule_condition_page/create.html",
        form=form
    )

# ===================== DETAIL =====================

@rule_condition_bp.route("/<int:id>")
@login_required
def detail(id: int):
    rule_condition = RuleConditionService.get_by_id(id)
    return render_template(
        "rule_condition_page/detail.html",
        rule_condition=rule_condition
    )

# ===================== EDIT =====================

@rule_condition_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id: int):
    # Fetch the existing rule condition
    rule_condition = RuleConditionService.get_by_id(id)

    # Pass rule_condition as required positional argument
    form = RuleConditionEditForm(rule_condition=rule_condition)

    # Pre-populate form fields on GET
    if request.method == "GET":
        form.rule_id.data = rule_condition.rule_id
        form.symptom_id.data = rule_condition.symptom_id
        form.is_active.data = rule_condition.is_active

    # On POST, validate and update
    if form.validate_on_submit():
        try:
            RuleConditionService.update(rule_condition, form.data)
            flash("Rule condition updated successfully.", "success")
            return redirect(url_for("rule_condition.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template(
        "rule_condition_page/edit.html",
        form=form,
        rule_condition=rule_condition
    )

# ===================== DELETE =====================

@rule_condition_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete(id: int):
    rule_condition = RuleConditionService.get_by_id(id)
    form = RuleConditionConfirmDeleteForm()

    if form.validate_on_submit():
        try:
            RuleConditionService.delete(rule_condition)
            flash("Rule condition deleted successfully.", "success")
            return redirect(url_for("rule_condition.index"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template(
        "rule_condition_page/delete_confirm.html",
        form=form,
        rule_condition=rule_condition
    )

# ===================== TOGGLE ACTIVE =====================

@rule_condition_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
def toggle(id: int):
    rule_condition = RuleConditionService.get_by_id(id)
    RuleConditionService.toggle_active(rule_condition)

    flash("Rule condition status updated.", "info")
    return redirect(url_for("rule_condition.index"))
