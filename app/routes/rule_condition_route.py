from collections import defaultdict
from app.models.rule_conditions import RuleConditionsTable
from extensions import db

from flask import (
    Blueprint, abort, render_template,
    redirect, session, url_for, flash, request
)
from flask_login import login_required

from app.forms.rule_condition_form import (
    RuleConditionCreateForm,
    RuleConditionEditForm,
    RuleConditionConfirmDeleteForm
)
from app.models.symptoms import SymptomsTable
from app.services.rule_condition_service import RuleConditionService
from app.decorators.access import role_required, permission_required
rule_condition_bp = Blueprint("rule_condition",__name__,url_prefix="/admin/rule-conditions")

# ===================== INDEX =====================

@rule_condition_bp.route("/")
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_RULE_CONDITION")
def index():
    try:
        page = request.args.get("page", 1, type=int)

        search = request.args.get(
            "search",
            "",
            type=str
        ).strip()

        active_value = request.args.get(
            "active",
            "",
            type=str
        ).strip()

        # Convert active filter to integer
        if active_value in ("0", "1"):
            active_only = int(active_value)
        else:
            active_only = None

        pagination = RuleConditionService.paginate(
            page=page,
            per_page=10,
            search=search if search else None,
            active_only=active_only
        )

        return render_template(
            "rule_condition_page/index.html",
            rule_conditions=pagination.items,
            pagination=pagination,
            search=search,
            active_only=active_only,
            grouped_symptoms=get_grouped_symptoms()
        )

    except Exception as e:

        print(f"Rule Condition Index Error: {e}")

        flash(
            "Unable to load rule conditions.",
            "danger"
        )

        return redirect(
            url_for("rule_condition.index")
        )

# ===================== CREATE =====================

@rule_condition_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("CREATE_RULE_CONDITION")
def create():
    form = RuleConditionCreateForm()

    if form.validate_on_submit():
        try:
            RuleConditionService.create(form.data)
            flash("Rule condition created successfully.", "success")
            return redirect(url_for("rule_condition.index"))
        except Exception as e:
            flash(str(e), "danger")


    # ទាញយក Symptom Data ជាមួយ Disease Information
    grouped_symptoms = RuleConditionService.get_symptoms_grouped_with_diseases()
    return render_template(
        "rule_condition_page/create.html",
        form=form,
        grouped_symptoms=grouped_symptoms
    )

# ===================== DETAIL =====================

@rule_condition_bp.route("/<int:id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("DETAIL_RULE_CONDITION")
def detail(id: int):
    rule_condition = RuleConditionService.get_by_id(id)
    return render_template(
        "rule_condition_page/detail.html",
        rule_condition=rule_condition,
        grouped_symptoms=get_grouped_symptoms()
    )

# ===================== EDIT =====================

@rule_condition_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("EDIT_RULE_CONDITION")
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
        rule_condition=rule_condition,
        grouped_symptoms=get_grouped_symptoms()
    )

# ===================== DELETE =====================

@rule_condition_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("DELETE_RULE_CONDITION")
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
        rule_condition=rule_condition,
        grouped_symptoms=get_grouped_symptoms()
    )

# ===================== TOGGLE ACTIVE =====================

@rule_condition_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("TOGGLE_RULE_CONDITION")
def toggle(id: int):
    rule_condition = RuleConditionService.get_by_id(id)
    RuleConditionService.toggle_active(rule_condition)

    flash("Rule condition status updated.", "info")
    return redirect(url_for("rule_condition.index"))

def get_grouped_symptoms():
    symptoms = db.session.execute(
        db.select(SymptomsTable).order_by(SymptomsTable.symptom_group)
    ).scalars().all()

    grouped = defaultdict(list)

    for s in symptoms:
        grouped[s.symptom_group].append((s.id, s.symptom_name))

    return grouped


@rule_condition_bp.route("/preview", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("PREVIEW_RULE_CONDITION")
def preview_rule_condition():

    data = session.get("rule_data")

    if not data:
        return redirect(url_for("rule_condition.create_rule_condition"))

    symptoms = db.session.execute(
        db.select(SymptomsTable).where(SymptomsTable.id.in_(data["symptoms"]))
    ).scalars().all()

    if request.method == "POST":

        new_rule = RuleConditionsTable(
            name=data["name"]
        )

        db.session.add(new_rule)
        db.session.flush()

        # link symptoms
        for s in symptoms:
            new_rule.symptoms.append(s)

        db.session.commit()
        session.pop("rule_data", None)

        return redirect(url_for("rule_condition.index"))
    return render_template(
        "rule_condition_page/preview.html",
        rule=data,
        symptoms=symptoms
    )