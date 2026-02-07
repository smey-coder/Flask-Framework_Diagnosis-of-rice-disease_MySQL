import json
from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from flask_login import login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash
from sqlalchemy import text

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
from app.services.diagnosis_service import DiagnosisService

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
    # Get all active symptoms
    symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    # Make sure IDs are integers
    form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

    if form.validate_on_submit():
        # Convert submitted data to integers
        selected_ids = [int(s) for s in form.symptoms.data or []]

        if not selected_ids:
            flash("Please select at least one symptom.", "warning")
            return redirect(url_for("user.diagnosis_input"))

        # Store IDs in session
        session["selected_symptoms"] = selected_ids

        # Store corresponding symptom NAMES for view filtering
        selected_symptoms = SymptomsTable.query.filter(SymptomsTable.id.in_(selected_ids)).all()
        session["selected_symptoms_names"] = [s.symptom_name for s in selected_symptoms]

        return redirect(url_for("user.diagnosis_result"))

    return render_template("user_page/index.html", form=form, user=current_user)

@user_bp.route("/save_diagnosis", methods=["POST"])
@login_required
def save_diagnosis_history(conclusions, rule_trace=None):
    """
    Save diagnosis results to the database using raw SQL.
    """
    if not conclusions:
        return

    insert_sql = text("""
        INSERT INTO tbl_diagnosis_history (
            user_id,
            user_name,
            disease_id,
            confidence,
            selected_symptoms,
            status,
            created_at
        )
        VALUES (
            :user_id,
            :user_name,
            :disease_id,
            :confidence,
            :selected_symptoms,
            :status,
            NOW()
        )
    """)

    # Convert selected symptom IDs to comma-separated string
    selected_symptoms = ",".join(str(s) for s in session.get("selected_symptoms", []))

    for disease_id, data in conclusions.items():
        confidence = data.get("certainty", 0.0)
        
        db.session.execute(
            insert_sql,
            {
                "user_id": current_user.id,
                "user_name": current_user.username,
                "disease_id": disease_id,
                "confidence": confidence,
                "selected_symptoms": selected_symptoms,
                "status": "Completed"
            }
        )

    db.session.commit()

@user_bp.route("/diagnosis/result")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    #Get selected symptoms
    selected_ids = session.get("selected_symptoms", [])
    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("user.diagnosis_input"))

    #Run inference
    conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

    # SAVE IN SESSION
    session["rule_trace"] = rule_trace

    if not conclusions:
        flash("No diseases matched your symptoms.", "info")
        return redirect(url_for("user.diagnosis_input"))

    # Save diagnosis results using raw SQL helper
    save_diagnosis_history(conclusions, rule_trace)

    #Prepare results for template
    results = []
    for disease_id, data in conclusions.items():
        disease = data["disease"]
        results.append({
            "disease_id": disease_id,
            "disease_name": getattr(disease, "disease_name", ""),
            "image": getattr(disease, "image", ""),
            "severity_level":  disease.severity_level if disease else None,
            "confidence": data.get("certainty", 0.0),
            "rules": rule_trace.get(str(disease_id), []),
            "explanation": getattr(disease, "explanation", ""),
        })

    # Render result template
    return render_template(
        "user_page/result.html",
        results=results,
        user=current_user
    )


@user_bp.route("/history")
@login_required
@role_required("User")
@permission_required("VIEW_HISTORY")
def diagnosis_history():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Query history from table or view
    sql = text("""
        SELECT *
        FROM view_diagnosis_history
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = db.session.execute(
        sql,
        {"user_id": current_user.id, "limit": per_page, "offset": offset}
    )
    histories = result.fetchall()

    # Count total rows
    count_sql = text("""
        SELECT COUNT(*) 
        FROM view_diagnosis_history
        WHERE user_id = :user_id
    """)
    total = db.session.execute(count_sql, {"user_id": current_user.id}).scalar()
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "user_page/history.html",
        histories=histories,
        page=page,
        total_pages=total_pages
    )
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
    selected_symptoms = [
        s.symptom_name
        for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
    ]

    #ADD THIS (Calculate confidence)
    overall_cf = logs[-1]["cf_after"] if logs else 0.0

    treatments = diagnosis_service.treatment_disease(disease_id)
    preventions = diagnosis_service.prevention_disease(disease_id)

    return render_template(
        "user_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        certainty=overall_cf,   # ✅ PASS TO TEMPLATE
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
