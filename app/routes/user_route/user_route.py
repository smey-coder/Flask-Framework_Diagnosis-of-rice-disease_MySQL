from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from flask_login import login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash

from app import services
from app.decorators.access import role_required, permission_required
from app.forms.diagnosis_form import DiagnosisForm
from app.forms.user_forms import UserEditForm
from app.models.diagnosis_history import DiagnosisHistoryTable
from app.models.diseases import DiseaseTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.rules import RulesTable
from app.models.symptoms import SymptomsTable
from extensions import db
from app.services.diagnosis_service import DiagnosisService
from app.services.rule_service import RuleService
from app.services.rule_condition_service import RuleConditionService

from app.models.rules import RulesTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.symptoms import SymptomsTable

# Create user blueprint
user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="../../templates")
diagnosis_service = DiagnosisService()

# ---------------- DASHBOARD ----------------
@user_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required("User")
def dashboard():
    default_disease = DiseaseTable.query.first()  # or choose a specific one
    return render_template("user_page/dashboard.html", user=current_user, disease=default_disease)

# ---------------- SETTINGS ----------------
@user_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("User")
@permission_required("USER_EDIT_ACCOUNT")
def settings():
    form = UserEditForm(original_user=current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data

        if form.password.data:
            current_user.password_hash = generate_password_hash(form.password.data)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user.settings"))

    if request.method == "GET":
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    return render_template("user_page/settings.html", form=form, user=current_user)

@user_bp.route("/settings/delete", methods=["POST"])
@login_required
@role_required("User")
@permission_required("USER_DELETE_ACCOUNT")
def delete_account():
    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash("Your account has been deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete account. Try again later.", "danger")
    return redirect(url_for("auth.login"))

# ---------------- ABOUT ----------------
@user_bp.route("/about")
@login_required
@role_required("User")
@permission_required("USER_ABOUT")
def about():
    about_info = {
        "app_name": "Rice Expert System",
        "version": "1.0.0",
        "developer": "San Reaksmey, Try Reaksmey, Pen Panhna, Tath Kongea",
        "email": "sanreaksmey01@gmail.com",
        "description": "Helps farmers diagnose rice diseases and manage treatments efficiently.",
    }
    return render_template("user_page/about.html", about=about_info)

# ---------------- DIAGNOSIS ----------------
@user_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_input():
    form = DiagnosisForm()
    symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

    if form.validate_on_submit():
        selected = form.symptoms.data or []
        if not selected:
            flash("Please select at least one symptom.", "warning")
            return redirect(url_for("user.diagnosis_input"))
        
        session["selected_symptoms"] = selected
        return redirect(url_for("user.diagnosis_result"))

    return render_template("user_page/index.html", form=form, user=current_user)

@user_bp.route("/diagnosis/result")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    selected_ids = session.get("selected_symptoms")

    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("user.diagnosis_input"))

    conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

    results = []

    for disease_id, data in conclusions.items():
        disease = data["disease"]
        cf = data["certainty"]   # ❗ REAL CF (0.0–1.0)

        logs = rule_trace.get(str(disease_id), [])

        results.append({
            "disease_id": disease_id,
            "disease": disease,
            "confidence": cf,
            "logs": logs
        })

        # ✅ SAVE HISTORY (NO 100% DEFAULT)
        history = DiagnosisHistoryTable(
            user_id=current_user.id,
            user_name=current_user.username,
            disease_id=disease_id,
            confidence=cf,   # store percentage OR store cf (choose one)
            status="Completed"
        )
        db.session.add(history)

    db.session.commit()

    return render_template(
        "user_page/result.html",
        results=results
    )



@user_bp.route("/history")
@login_required
@role_required("User")
@permission_required("VIEW_HISTORY")
def diagnosis_history():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    pagination = DiagnosisHistoryTable.query.filter_by(user_id=current_user.id)\
        .order_by(DiagnosisHistoryTable.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template("user_page/history.html", histories=pagination.items, pagination=pagination, user=current_user)

# ---------------- DIAGNOSIS EXPLANATION ----------------
@user_bp.route("/diagnosis/explain/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(disease_id):
    rule_trace = session.get("rule_trace")
    if not rule_trace:
        flash("Please perform diagnosis first.", "warning")
        return redirect(url_for("user.diagnosis_input"))

    logs = diagnosis_service.explain_disease(disease_id, rule_trace)
    if not logs:
        flash("No explanation available for this disease.", "info")
        return redirect(url_for("user.diagnosis_result"))

    disease = DiseaseTable.query.get_or_404(disease_id)
    symptom_ids = session.get("selected_symptoms") or []
    selected_symptoms = [s.symptom_name for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()]

    treatments = diagnosis_service.treatment_disease(disease_id)
    preventions = diagnosis_service.prevention_disease(disease_id)

    return render_template(
        "user_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        user=current_user
    )

# ---------------- TREATMENT & PREVENTION ----------------
@user_bp.route("/diagnosis/treatment/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def disease_treatment(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    treatments = diagnosis_service.treatment_disease(disease_id)
    return render_template("user_page/treatment.html", disease=disease, treatments=treatments, user=current_user)

@user_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def disease_prevention(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    preventions = diagnosis_service.prevention_disease(disease_id)
    return render_template("user_page/prevention.html", disease=disease, preventions=preventions, user=current_user)
