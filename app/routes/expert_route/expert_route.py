from venv import logger
from flask import Blueprint, abort, current_app, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from app.forms.rule_form import RuleCreateForm, RuleEditForm
from app.forms.symptom_forms import SymptomEditForm
from app.services.rule_service import RuleService
from app.services.symptom_service import SymptomService
from extensions import db
from werkzeug.security import generate_password_hash
from app.decorators.access import role_required, permission_required
from app.models.rule_conditions import RuleConditionsTable
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.forms.user_forms import UserEditForm
from app.forms.diseases import DiseaseEditForm, DiseaseSearchForm
from app.forms.diagnosis_form import DiagnosisForm
from app.services.diagnosis_service import DiagnosisService
from app.services.disease_service import DiseaseService

expert_bp = Blueprint(
    "expert", __name__, url_prefix="/expert", template_folder="../../templates"
)
service = DiagnosisService()

# ---------------- DASHBOARD ----------------
@expert_bp.route("/dashboard")
@login_required
@role_required("Expert")
def dashboard():
    stats = {
        "rule_conditions": RuleConditionsTable.query.count(),
        "diseases": DiseaseTable.query.count(),
        "symptoms": SymptomsTable.query.count(),
        "rules": RulesTable.query.count()
    }
    return render_template("expert_page/dashboard.html", user=current_user, stats=stats)


# ---------------- SETTINGS / PROFILE ----------------
@expert_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_PROFILE")
def settings():
    form = UserEditForm(original_user=current_user)

    if form.validate_on_submit():
        try:
            current_user.username = form.username.data
            current_user.full_name = form.full_name.data
            if form.password.data:
                current_user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Failed to update profile. Try again later.", "danger")
        return redirect(url_for("expert.settings"))

    # Pre-fill form fields on GET
    if request.method == "GET":
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name

    return render_template("expert_page/settings.html", form=form, user=current_user)


@expert_bp.route("/settings/delete", methods=["POST"])
@login_required
@role_required("Expert")
@permission_required("DELETE_USER_ACCOUNT")
def delete_account():
    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash("Your account has been deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete account. Try again later.", "danger")
    return redirect(url_for("auth.login"))


# ---------------- ABOUT ----------------
@expert_bp.route("/about")
@login_required
@role_required("Expert")
def about():
    about_info = {
        "app_name": "Rice Expert System",
        "version": "1.0.0",
        "developer": "SanReaksmey",
        "email": "sanreaksmey01@gmail.com",
        "description": "This system helps farmers diagnose rice diseases and manage treatments efficiently.",
    }
    return render_template("expert_page/about.html", about=about_info)


# ---------------- DIAGNOSIS ----------------
@expert_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_input():
    form = DiagnosisForm()
    symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

    if form.validate_on_submit():
        selected = form.symptoms.data or []
        if not selected:
            flash("Please select at least one symptom.", "warning")
            return redirect(url_for("expert.diagnosis_input"))

        session["selected_symptoms"] = selected
        return redirect(url_for("expert.diagnosis_result"))

    return render_template("expert_page/index.html", form=form, user=current_user)


@expert_bp.route("/diagnosis/result")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    selected_ids = session.get("selected_symptoms")
    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("expert.diagnosis_input"))

    conclusions, rule_trace, skipped_rules = service.infer(selected_ids)
    if not conclusions:
        flash("No diseases matched your symptoms.", "info")
        return redirect(url_for("expert.diagnosis_input"))

    session["rule_trace"] = rule_trace
    session["skipped_rules"] = skipped_rules

    return render_template("expert_page/result.html", conclusions=conclusions, user=current_user)


@expert_bp.route("/diagnosis/explain/<int:disease_id>")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(disease_id):
    rule_trace = session.get("rule_trace")
    if not rule_trace:
        flash("Please perform diagnosis first.", "warning")
        return redirect(url_for("expert.diagnosis_input"))

    logs = service.explain_disease(disease_id, rule_trace)
    if not logs:
        flash("No explanation available for this disease.", "info")
        return redirect(url_for("expert.diagnosis_result"))

    disease = DiseaseTable.query.get_or_404(disease_id)
    symptom_ids = session.get("selected_symptoms") or []
    selected_symptoms = [
        s.symptom_name for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
    ]

    treatments = service.treatment_disease(disease_id)
    preventions = service.prevention_disease(disease_id)

    return render_template(
        "expert_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        user=current_user
    )

# ---------- TREATMENT & PREVENTION ----------
@expert_bp.route("/diagnosis/treatment/<int:disease_id>")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def disease_treatment(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    treatments = service.treatment_disease(disease_id)
    return render_template(
        "expert_page/treatment.html",
        disease=disease,
        treatments=treatments,
        user=current_user
    )

@expert_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def disease_prevention(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    preventions = service.prevention_disease(disease_id)
    return render_template(
        "expert_page/prevention.html",
        disease=disease,
        preventions=preventions,
        user=current_user
    )


# ---------------- DISEASE MANAGEMENT ----------------
@expert_bp.route("/disease")
@login_required
@role_required("Expert")
@permission_required("VIEW_DISEASE")
def index_disease():
    page = request.args.get("page", 1, type=int)
    search_form = DiseaseSearchForm(request.args, meta={"csrf": False})

    query = DiseaseTable.query

    # Filters
    name = request.args.get("disease_name", "").strip()
    dtype = request.args.get("disease_type", "").strip()
    severity = request.args.get("severity_level", "").strip()

    if name:
        query = query.filter(DiseaseTable.disease_name.ilike(f"%{name}%"))
    if dtype:
        query = query.filter(DiseaseTable.disease_type == dtype)
    if severity:
        query = query.filter(DiseaseTable.severity_level == severity)

    diseases = query.order_by(DiseaseTable.id.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "expert_page/index_disease.html",
        diseases=diseases,
        search_form=search_form,
        current_user=current_user
    )


@expert_bp.route("/detail/disease/<int:disease_id>")
@login_required
@role_required("Expert")
@permission_required("VIEW_DISEASE")
def detail_disease(disease_id):
    disease = DiseaseService.get_disease_by_id(disease_id)
    if not disease:
        flash("Disease not found.", "warning")
        abort(404)
    return render_template(
        "expert_page/detail_disease.html",
        disease=disease,
        current_user=current_user
    )


@expert_bp.route("/edit/disease/<int:disease_id>", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_DISEASE")
def edit_disease(disease_id):
    disease = DiseaseService.get_disease_by_id(disease_id)
    if not disease:
        flash("Disease not found.", "warning")
        abort(404)

    form = DiseaseEditForm(disease)

    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data.strip(),
            "disease_type": form.disease_type.data.strip(),
            "description": form.description.data.strip() if form.description.data else "",
            "severity_level": form.severity_level.data.strip() if form.severity_level.data else "Low",
            "image": form.image.data if form.image.data else disease.image,
            "is_active": form.is_active.data
        }

        updated = DiseaseService.update_disease(disease_id, data)
        if updated:
            flash(f"Disease '{updated.disease_name}' updated successfully.", "success")
            return redirect(url_for("expert.detail_disease", disease_id=disease_id))
        else:
            flash("Failed to update disease. Try again.", "danger")

    # Pre-fill form fields
    if request.method == "GET":
        form.disease_name.data = disease.disease_name
        form.disease_type.data = disease.disease_type
        form.severity_level.data = disease.severity_level
        form.description.data = disease.description
        form.is_active.data = disease.is_active

    return render_template("expert_page/edit_disease.html", form=form, disease=disease)

#----------------- Expert symptom route ------------------
@expert_bp.route("/symptom", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("VIEW_SYMPTOM")
def index_symptom():
    symptoms = SymptomService.get_symptom_all()
    return render_template("expert_page/index_symptom.html", symptoms=symptoms)

@expert_bp.route("/<int:symptom_id>")
@login_required
@role_required("Expert")
@permission_required("VIEW_SYMPTOM")
def detail_symptom(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)
    return render_template("expert_page/detail_symptom.html", symptom=symptom)


@expert_bp.route("/<int:symptom_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_SYMPTOM")
def edit_symptom(symptom_id: int):
    symptom = SymptomService.get_symptom_by_id(symptom_id)
    if symptom is None:
        abort(404)
    
    form = SymptomEditForm(original_symptom=symptom, obj=symptom)
    if form.validate_on_submit():
        data = {
            "symptom_name": form.symptom_name.data,
            "symptom_group": form.symptom_group.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }
        SymptomService.update_symptom(symptom, data)
        flash(f"Symptom '{symptom.symptom_name}' was updated successfully.", "success")
        return redirect(url_for("expert.detail_symptom", symptom_id=symptom.id))
    
    return render_template("expert_page/edit_symptom.html", form=form, symptom=symptom)


# ------------- Manager Rule ---------------
# ========================= INDEX =========================
@expert_bp.route("/rule/")
@login_required
@role_required("Expert")
@permission_required("VIEW_RULE")
def index_rule():
    """Display all rules"""
    rules = RuleService.get_all_rules()
    return render_template(
        "expert_page/rule_pages/index.html",
        rules=rules,
        user=current_user
    )

# ========================= DETAIL =========================
@expert_bp.route("/rule/<int:rule_id>")
@login_required
@role_required("Expert")
@permission_required("VIEW_RULE")
def detail_rule(rule_id):
    """View rule detail"""
    rule = RuleService.get_rule_by_id(rule_id)
    if not rule:
        abort(404)
    return render_template("expert_page/rule_pages/detail.html", rule=rule)

# ========================= EDIT =========================
@expert_bp.route("/rule/<int:rule_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_RULE")
def edit_rule(rule_id):
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
            return redirect(url_for("expert.index_rule"))
        except Exception as e:
            current_app.logger.error(f"Error updating rule: {e}")
            flash(f"Error updating rule: {e}", "danger")

    return render_template("expert_page/rule_pages/edit.html", form=form, rule=rule)

# ========================= CREATE =========================
@expert_bp.route("/rule/create", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("CREATE_RULE")
def create_rule():
    """Create a new rule"""
    form = RuleCreateForm()
    form.disease_id.choices = [(d.id, d.disease_name) for d in DiseaseTable.query.all()]

    if form.validate_on_submit():
        try:
            rule = RuleService.create_rule(form)
            flash(f"Rule #{rule.id} created successfully!", "success")
            return redirect(url_for("expert.index_rule"))
        except Exception as e:
            current_app.logger.error(f"Error creating rule: {e}")
            flash(f"Error creating rule: {e}", "danger")

    return render_template("expert_page/rule_pages/create.html", form=form)