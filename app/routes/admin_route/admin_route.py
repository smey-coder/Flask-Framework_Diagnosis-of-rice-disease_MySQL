from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from functools import wraps
from app.forms.diagnosis_form import DiagnosisForm
from app.models.symptoms import SymptomsTable
from app.models.diseases import DiseaseTable
from app.services.diagnosis_service import DiagnosisService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../../templates")
service = DiagnosisService()


# ---------- ACCESS CONTROL ----------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.has_role("Admin"):
            flash("No permission", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated


# ---------- DASHBOARD ----------
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template("admin_page/dashboard.html", user=current_user)


# ---------- DIAGNOSIS INPUT ----------
@admin_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@admin_required
def diagnosis_input():
    form = DiagnosisForm()
    symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

    if form.validate_on_submit():
        selected = form.symptoms.data or []
        if not selected:
            flash("Please select at least one symptom.", "warning")
            return redirect(url_for("admin.diagnosis_input"))

        session["selected_symptoms"] = selected
        return redirect(url_for("admin.diagnosis_result"))

    form.symptoms.data = form.symptoms.data or []
    return render_template("diagnosis_page/index.html", form=form, user=current_user)


# ---------- DIAGNOSIS RESULT ----------
@admin_bp.route("/diagnosis/result")
@login_required
@admin_required
def diagnosis_result():
    selected_ids = session.get("selected_symptoms")
    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("admin.diagnosis_input"))

    conclusions, rule_trace, skipped_rules = service.infer(selected_ids)
    if not conclusions:
        flash("No diseases matched your symptoms.", "info")
        return redirect(url_for("admin.diagnosis_input"))

    session["rule_trace"] = rule_trace
    session["skipped_rules"] = skipped_rules

    return render_template(
        "diagnosis_page/result.html",
        conclusions=conclusions,
        user=current_user
    )


# ---------- DIAGNOSIS EXPLANATION ----------
@admin_bp.route("/diagnosis/explain/<int:disease_id>")
@login_required
@admin_required
def diagnosis_explain(disease_id):
    rule_trace = session.get("rule_trace")
    if not rule_trace:
        flash("Please perform diagnosis first.", "warning")
        return redirect(url_for("admin.diagnosis_input"))

    logs = service.explain_disease(disease_id, rule_trace)
    if not logs:
        flash("No explanation available for this disease.", "info")
        return redirect(url_for("admin.diagnosis_result"))

    disease = DiseaseTable.query.get_or_404(disease_id)
    symptom_ids = session.get("selected_symptoms") or []
    selected_symptoms = [s.symptom_name for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()]

    treatments = service.treatment_disease(disease_id)
    preventions = service.prevention_disease(disease_id)

    return render_template(
        "diagnosis_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        user=current_user
    )


# ---------- TREATMENT & PREVENTION ----------
@admin_bp.route("/diagnosis/treatment/<int:disease_id>")
@login_required
@admin_required
def disease_treatment(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    treatments = service.treatment_disease(disease_id)
    return render_template("diagnosis_page/treatment.html", 
                           disease=disease, 
                           treatments=treatments, 
                           user=current_user)


@admin_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@admin_required
def disease_prevention(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    preventions = service.prevention_disease(disease_id)
    return render_template("diagnosis_page/prevention.html", disease=disease, 
                           preventions=preventions, 
                           user=current_user)
