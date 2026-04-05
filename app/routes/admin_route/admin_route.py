from flask import Blueprint, abort, current_app, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from functools import wraps

import requests
from app.forms.diagnosis_form import DiagnosisForm
from app.models.symptoms import SymptomsTable
from app.models.diseases import DiseaseTable
from app.services import diagnosis_service
from app.services.diagnosis_service import DiagnosisService
from app.models.user import UserTable
from app.models.rules import RulesTable
from app.services.user_service import UserService
from extensions import db
from werkzeug.security import generate_password_hash
from app.forms.user_forms import UserEditForm
from app.models.role import RoleTable
from app.decorators.access import role_required, permission_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../../templates")
service = DiagnosisService()

# Use city IDs instead of names
CAMBODIA_CITIES = [
    {"id": 1821305, "name": "Phnom Penh"},
    {"id": 1821479, "name": "Siem Reap"},
    {"id": 1820855, "name": "Battambang"},
    {"id": 1820848, "name": "Sihanoukville"},
    {"id": 1821383, "name": "Kampong Cham"},
    {"id": 1821381, "name": "Kampong Speu"},
    {"id": 1821378, "name": "Kampong Thom"},
    {"id": 1821358, "name": "Kandal"},
    {"id": 1821416, "name": "Takeo"},
    {"id": 1821399, "name": "Prey Veng"},
    {"id": 1821407, "name": "Kampot"},
    {"id": 1821400, "name": "Kratie"},
    {"id": 1821391, "name": "Banteay Meanchey"},
    {"id": 1821390, "name": "Pursat"},
    {"id": 1821389, "name": "Oddar Meanchey"},
    {"id": 1821388, "name": "Kep"},
    {"id": 1821387, "name": "Mondulkiri"},
    {"id": 1821386, "name": "Ratanakiri"},
    {"id": 1821385, "name": "Stung Treng"},
    {"id": 1821384, "name": "Svay Rieng"},
]


# =========================
# LANGUAGE SWITCH
# =========================
@admin_bp.route("/set-language", methods=["POST"])
def set_language():
    lang = request.form.get("lang")

    if lang in ["en", "km"]:
        session["lang"] = lang

    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def dashboard():
    from app.forms.weather_form import CitySearchForm
    from app.services.weather_service import WeatherService

    stats = {
        "users": UserTable.query.count(),
        "diseases": DiseaseTable.query.count(),
        "symptoms": SymptomsTable.query.count(),
        "rules": RulesTable.query.count()
    }

    form = CitySearchForm()
    search_results = []
    selected_city_weather = None

    # Check if a city was selected for weather
    selected_city_id = request.args.get('city_id')
    if selected_city_id:
        selected_city_weather = WeatherService.get_weather(selected_city_id)

    if form.validate_on_submit():
        selected_city_name = form.city.data
        if selected_city_name:
            selected_city_weather = WeatherService.get_weather(selected_city_name)

    return render_template(
        "admin_page/dashboard.html",
        user=current_user,
        stats=stats,
        form=form,
        search_results=search_results,
        selected_city_weather=selected_city_weather
    )
# ---------- SETTINGS / PROFILE ----------
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Admin")
@permission_required("PERMISSION_MANAGER_SYSTEM")
def settings():
    from app.forms.user_forms import UserEditForm
    
    # Pass the current_user as original_user
    form = UserEditForm(original_user=current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data

        if form.password.data:
            from werkzeug.security import generate_password_hash
            current_user.password_hash = generate_password_hash(form.password.data)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("admin.settings"))

    # Pre-fill the form fields
    if request.method == "GET":
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    return render_template("admin_page/settings.html", form=form)

# ---------- ABOUT PAGE ----------
@admin_bp.route("/about")
@login_required
@role_required("Admin")
@permission_required("PERMISSION_MANAGER_SYSTEM")
def about():
    about_info = {
        "app_name": "Rice Expert System",
        "version": "1.0.0",
        "developer": "San Reaksmey, Try Reaksmey, Pen Panhna, Tath Kongea",
        "email": "sanreaksmey01@gmail.com",
        "description": "This system helps farmers diagnose rice diseases and manage treatments efficiently.",
    }
    return render_template("admin_page/about.html", about=about_info)


# ---------- DIAGNOSIS INPUT ----------
@admin_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@role_required("Admin")
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
            return redirect(url_for("admin.diagnosis_input"))

        # Store IDs in session
        session["selected_symptoms"] = selected_ids

        # Store corresponding symptom NAMES for view filtering
        selected_symptoms = SymptomsTable.query.filter(SymptomsTable.id.in_(selected_ids)).all()
        session["selected_symptoms_names"] = [s.symptom_name for s in selected_symptoms]

        return redirect(url_for("admin.diagnosis_result"))

    return render_template("diagnosis_page/index.html", form=form, user=current_user)


# ---------- DIAGNOSIS RESULT ----------
@admin_bp.route("/diagnosis/result")
@login_required
@role_required("Admin")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    #Get selected symptoms
    selected_ids = session.get("selected_symptoms", [])
    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("admin.diagnosis_input"))

    #Run inference
    conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

    # SAVE IN SESSION
    session["rule_trace"] = rule_trace

    if not conclusions:
        flash("No diseases matched your symptoms.", "info")
        return redirect(url_for("admin.diagnosis_input"))

    # Save diagnosis results using raw SQL helper
    #save_diagnosis_history(conclusions, rule_trace)

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
        "diagnosis_page/result.html",
        results=results,
        user=current_user
    )


# ---------- DIAGNOSIS EXPLANATION ----------
@admin_bp.route("/diagnosis/explain/<int:disease_id>")
@login_required
@role_required("Admin")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(disease_id):
    rule_trace = session.get("rule_trace")
    if not rule_trace:
        flash("Please perform diagnosis first.", "warning")
        return redirect(url_for("admin.diagnosis_input"))

    logs = diagnosis_service.DiagnosisService.explain_disease(disease_id, rule_trace)
    if not logs:
        flash("No explanation available for this disease.", "info")
        return redirect(url_for("admin.diagnosis_result"))

    disease = DiseaseTable.query.get_or_404(disease_id)

    symptom_ids = session.get("selected_symptoms") or []
    selected_symptoms = [
        s.symptom_name
        for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
    ]

    #ADD THIS (Calculate confidence)
    overall_cf = logs[-1]["cf_after"] if logs else 0.0

    treatments = diagnosis_service.DiagnosisService.treatment_disease(disease_id)
    preventions = diagnosis_service.DiagnosisService.prevention_disease(disease_id)

    return render_template(
        "diagnosis_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        certainty=overall_cf,   # ✅ PASS TO TEMPLATE
        user=current_user
    )


# ---------- TREATMENT & PREVENTION ----------
@admin_bp.route("/diagnosis/treatment/<int:disease_id>")
@login_required
@role_required("Admin")
@permission_required("RUN_DIAGNOSIS")
def disease_treatment(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    treatments = service.treatment_disease(disease_id)
    return render_template(
        "diagnosis_page/treatment.html",
        disease=disease,
        treatments=treatments,
        user=current_user
    )


@admin_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@role_required("Admin")
@permission_required("RUN_DIAGNOSIS")
def disease_prevention(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    preventions = service.prevention_disease(disease_id)
    return render_template(
        "diagnosis_page/prevention.html",
        disease=disease,
        preventions=preventions,
        user=current_user
    )
