from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, current_app, abort
)
from flask_login import current_user, login_required
from app.models.diseases import DiseaseTable
from app.forms.rule_form import (
    RuleCreateForm,
    RuleEditForm,
    RuleConfirmDelete
)
from app.services.rule_service import RuleService

rule_bp = Blueprint("rules", __name__, url_prefix="/rules")


# ========================= INDEX =========================
@rule_bp.route("/")
@login_required
def index():
    """Display all rules"""
    rules = RuleService.get_all_rules()
    return render_template(
        "rule_page/index.html",
        rules=rules,
        user=current_user
    )


# ========================= CREATE =========================
@rule_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new rule"""
    form = RuleCreateForm()
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            rule = RuleService.create_rule(form)
            flash(f"Rule #{rule.id} created successfully!", "success")
            return redirect(url_for("rules.index"))
        except Exception as e:
            current_app.logger.error(f"Error creating rule: {e}")
            flash(f"Error creating rule: {e}", "danger")

    return render_template("rule_page/create.html", form=form)


# ========================= DETAIL =========================
@rule_bp.route("/<int:rule_id>")
@login_required
def detail(rule_id):
    """View rule detail"""
    rule = RuleService.get_rule_by_id(rule_id)
    if not rule:
        abort(404)
    return render_template("rule_page/detail.html", rule=rule)


# ========================= EDIT =========================
@rule_bp.route("/<int:rule_id>/edit", methods=["GET", "POST"])
@login_required
def edit(rule_id):
    """Edit rule"""
    rule = RuleService.get_rule_by_id(rule_id)
    if not rule:
        abort(404)

    form = RuleEditForm(obj=rule)
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            RuleService.update_rule(rule, form)
            flash(f"Rule #{rule.id} updated successfully!", "success")
            return redirect(url_for("rules.index"))
        except Exception as e:
            current_app.logger.error(f"Error updating rule: {e}")
            flash(f"Error updating rule: {e}", "danger")

    return render_template("rule_page/edit.html", form=form, rule=rule)


# ========================= DELETE =========================
@rule_bp.route("/<int:rule_id>/delete", methods=["GET", "POST"])
@login_required
def delete(rule_id):
    """Delete a rule by ID"""
    # Fetch the rule with eager-loaded disease to prevent DetachedInstanceError
    rule = RuleService.get_rule_by_id(rule_id)
    if not rule:
        abort(404)

    form = RuleConfirmDelete()

    if form.validate_on_submit():
        try:
            RuleService.delete_rule(rule)
            flash(f"Rule #{rule.id} deleted successfully!", "success")
            return redirect(url_for("rules.index"))

        except Exception as e:
            current_app.logger.error(f"Error deleting rule: {e}")
            flash(f"Error deleting rule: {e}", "danger")

    return render_template(
        "rule_page/delete_confirm.html",
        rule=rule,
        form=form
    )
