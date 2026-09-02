from collections import Counter
import csv
from datetime import datetime
import zoneinfo
import json
import os
from venv import logger

from flask import Blueprint, abort, current_app, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from functools import wraps

import pytz
import requests
from sqlalchemy import func, or_, text
from sqlalchemy.orm import joinedload
from app.forms.diagnosis_form import DiagnosisForm
from app.models import user
from app.models.diagnosis_history import DiagnosisHistoryTable
from app.models.permission import PermissionTable
from app.models.preventions import PreventionTable
from app.models.symptoms import SymptomsTable
from app.models.diseases import DiseaseTable
from app.models.treatments import TreatmentTable
# from app.services import diagnosis_service
# from app.services import diagnosis_service
from app.services.diagnosis_service import DiagnosisService
from app.models.user import UserTable
from app.models.rules import RulesTable
from app.services.user_service import UserService
from extensions import db
from app.services.audit_service import get_audit_file_path, log_audit
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms.user_forms import UserEditForm, UserProfileForm
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
@role_required("Admin", "Expert")
@permission_required("VIEW_DASHBOARD")
def dashboard():
    from app.forms.weather_form import CitySearchForm
    from app.services.weather_service import WeatherService

    stats = {
        "users": UserTable.query.count(),
        "roles": RoleTable.query.count(),
        "permissions": PermissionTable.query.count(),
        "diseases": DiseaseTable.query.count(),
        "symptoms": SymptomsTable.query.count(),
        "rules": RulesTable.query.count(),
        "treatments": TreatmentTable.query.count(),
        "preventions": PreventionTable.query.count(),
        "diagnosis": DiagnosisHistoryTable.query.count()
    }
    auth_logs = []
    file_path = get_audit_file_path()

    if os.path.exists(file_path):
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                auth_logs = list(reader)
        except Exception as e:
            print(f"Error reading audit CSV log: {e}")

    # Add calculated stats matching your CSV headers: action, email, ip_address
    stats["total_logs"] = len(auth_logs)
    stats["login_success"] = sum(1 for log in auth_logs if log.get("action") == "LOGIN_SUCCESS")
    stats["login_failed"] = sum(1 for log in auth_logs if log.get("action") == "LOGIN_FAILED")

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
        auth_logs=auth_logs,      # Recommended variable name
        log_audit=auth_logs,
        form=form,
        search_results=search_results,
        selected_city_weather=selected_city_weather
    )
#Report
@admin_bp.route("/admin/report", methods=["GET"])
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_REPORT_ADMIN")
def admin_report():
    # 1. Flexible Role Checking (Admin only)
    user_roles = [r.name.lower() for r in current_user.roles if r.name]
    if 'admin' not in user_roles:
        flash("អ្នកមិនមានសិទ្ធិចូលមើលទំព័រនេះទេ! (Admin Access Required)", "danger")
        return redirect(url_for('admin.dashboard'))

    # 2. Total System Metrics
    total_users = UserTable.query.count()
    total_diagnoses = DiagnosisHistoryTable.query.count()
    
    # 3. Top 5 Frequent Diseases (JOIN DiagnosisHistoryTable -> DiseaseTable)
    top_diseases = db.session.query(
        DiseaseTable.disease_name, 
        func.count(DiagnosisHistoryTable.id).label('count')
    ).join(DiseaseTable, DiagnosisHistoryTable.disease_id == DiseaseTable.id)\
     .group_by(DiseaseTable.id, DiseaseTable.disease_name)\
     .order_by(func.count(DiagnosisHistoryTable.id).desc())\
     .limit(5).all()

    # 4. Severity Distribution Mapping (JOIN DiagnosisHistoryTable -> DiseaseTable)
    severity_stats_raw = db.session.query(
        DiseaseTable.severity_level, 
        func.count(DiagnosisHistoryTable.id)
    ).join(DiseaseTable, DiagnosisHistoryTable.disease_id == DiseaseTable.id)\
     .group_by(DiseaseTable.severity_level).all()

    # Convert query list of tuples into a clean dictionary
    severity_stats = {severity: count for severity, count in severity_stats_raw if severity}

    return render_template(
        "admin_page/reports/admin_report.html",
        total_users=total_users,
        total_diagnoses=total_diagnoses,
        top_diseases=top_diseases,
        severity_stats=severity_stats,
        current_time=datetime.now().strftime("%d %b %Y, %I:%M %p")
    )


@admin_bp.route("/expert/report", methods=["GET"])
@login_required
@role_required("Admin", "Expert")
@permission_required("VIEW_REPORT_EXPERT")
def expert_report():
    # 1. Role Authorization (Requires 'expert' or 'admin')
    user_roles = [r.name.lower() for r in current_user.roles if r.name]
    if not any(role in user_roles for role in ['expert', 'admin']):
        flash("អ្នកមិនមានសិទ្ធិចូលមើលទំព័រនេះទេ! (Expert Access Required)", "danger")
        return redirect(url_for('admin.dashboard'))

    # 2. Extract Query Parameters for Filtering
    search_query = request.args.get('q', '').strip()
    selected_severity = request.args.get('severity', '').strip()

    # 3. Base Query: Join Diagnosis History with Diseases Table
    query = db.session.query(DiagnosisHistoryTable, DiseaseTable)\
        .join(DiseaseTable, DiagnosisHistoryTable.disease_id == DiseaseTable.id)

    # Filter by selected severity, or default to filtering High/Very High severity records
    if selected_severity:
        query = query.filter(DiseaseTable.severity_level == selected_severity)
    else:
        query = query.filter(DiseaseTable.severity_level.ilike('%high%'))

    # Text Search Filter (User Name or Disease Name)
    if search_query:
        query = query.filter(
            or_(
                DiagnosisHistoryTable.user_name.ilike(f'%{search_query}%'),
                DiseaseTable.disease_name.ilike(f'%{search_query}%')
            )
        )

    high_risk_cases = query.order_by(DiagnosisHistoryTable.created_at.desc()).all()

    # 4. Count Total Completed Diagnostic Cases
    reviewed_cases = DiagnosisHistoryTable.query.filter(
        DiagnosisHistoryTable.status == "Completed"
    ).count()

    # 5. Pre-resolve Symptom Names in Python
    # Create lookup map {id: name} from SymptomTable
    symptom_map = {s.id: s.symptom_name for s in SymptomsTable.query.all()}
    
    processed_cases = []
    for case, disease in high_risk_cases:
        # Extract symptom IDs using safe helper or raw column
        if hasattr(case, 'get_symptoms'):
            try:
                raw_ids = case.get_symptoms()
            except Exception:
                raw_ids = [case.selected_symptoms]
        else:
            raw_ids = [case.selected_symptoms]

        # Ensure raw_ids is an iterable list
        if isinstance(raw_ids, (int, str)):
            raw_ids = [raw_ids]
        elif not isinstance(raw_ids, (list, tuple)):
            raw_ids = []

        # Convert IDs to readable symptom names
        names = []
        for sid in raw_ids:
            try:
                clean_id = int(sid)
                if clean_id in symptom_map:
                    names.append(symptom_map[clean_id])
            except (ValueError, TypeError):
                # If sid is already a name string (not an ID)
                if isinstance(sid, str) and sid.strip():
                    names.append(sid.strip())

        symptom_str = ', '.join(names) if names else (case.selected_symptoms or 'N/A')

        processed_cases.append({
            'case': case,
            'disease': disease,
            'symptom_str': symptom_str
        })
        # 1. Aggregate Disease Frequency for Chart
    disease_counts = Counter()
    for case, disease in high_risk_cases:
        disease_name = disease.disease_name if disease else "Unknown"
        disease_counts[disease_name] += 1

    # Extract labels and values
    chart_labels = list(disease_counts.keys())
    chart_values = list(disease_counts.values())

    # 6. Render Template with Context
    return render_template(
        "admin_page/reports/expert_report.html",
        processed_cases=processed_cases,
        high_risk_cases=high_risk_cases,  # Retained for count calculations
        reviewed_cases=reviewed_cases,
        search_query=search_query,
        selected_severity=selected_severity,
        chart_labels_json=json.dumps(chart_labels),
        chart_values_json=json.dumps(chart_values),
        current_time=datetime.now().strftime("%d %b %Y, %I:%M %p")
    )
# ---------- SETTINGS / PROFILE ----------
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert", "User")
@permission_required("VIEW_SETTING")
def settings():
    form = UserProfileForm(obj=current_user)
    if request.method == "POST":
        try:
            # =========================
            # BASIC INFO UPDATE
            # =========================
            current_user.username = form.username.data.strip()
            current_user.email = form.email.data.strip()
            current_user.full_name = form.full_name.data.strip()

            # =========================
            # PASSWORD VALUES (USE ONLY FORM, NOT request.form)
            # =========================
            old_password = form.old_password.data
            new_password = form.password.data
            confirm_password = form.confirm_password.data

            # =========================
            # PASSWORD CHANGE LOGIC
            # =========================
            if new_password:

                # check confirm password (IMPORTANT)
                if new_password != confirm_password:
                    flash("Passwords do not match", "danger")
                    return redirect(url_for("admin.settings"))

                # must enter old password
                if not old_password:
                    flash("You must enter your old password", "danger")
                    return redirect(url_for("admin.settings"))

                # verify old password
                if not check_password_hash(current_user.password_hash, old_password):
                    flash("Old password is incorrect", "danger")
                    return redirect(url_for("admin.settings"))

                # update password
                current_user.password_hash = generate_password_hash(new_password)

            # =========================
            # SAVE DATABASE
            # =========================
            before_data = {
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
            }
            db.session.commit()
            after_data = {
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
            }
            log_audit(
                "UPDATE",
                "users",
                current_user.id,
                before_data=before_data,
                after_data=after_data,
            )

            flash("Profile updated successfully!", "success")
            return redirect(url_for("admin.settings"))

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while updating profile.", "danger")
            print("[ERROR]:", e)

    return render_template(
        "admin_page/settings.html",
        form=form,
        user=current_user
    )

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

def save_diagnosis_history(
    conclusions,
    rule_trace=None,
    monitoring_id=None
):
    """
    Save diagnosis results to tbl_diagnosis_history.

    Returns:
        list[int]: IDs of created diagnosis histories.
    """

    try:

        # =====================================================
        # VALIDATE
        # =====================================================

        if not conclusions:
            return []


        # =====================================================
        # INSERT SQL
        # =====================================================

        insert_sql = text("""
            INSERT INTO tbl_diagnosis_history (
                user_id,
                user_name,
                disease_id,
                confidence,
                monitoring_id,
                selected_symptoms,
                status,
                created_at
            )
            VALUES (
                :user_id,
                :user_name,
                :disease_id,
                :confidence,
                :monitoring_id,
                :selected_symptoms,
                :status,
                NOW()
            )
        """)


        # =====================================================
        # SELECTED SYMPTOMS
        # =====================================================

        selected_symptoms = ",".join(
            str(s)
            for s in session.get(
                "selected_symptoms",
                []
            )
        )


        # =====================================================
        # STORE CREATED IDS
        # =====================================================

        diagnosis_ids = []


        # =====================================================
        # INSERT
        # =====================================================

        for disease_id, data in conclusions.items():

            confidence = data.get(
                "certainty",
                0.0
            )


            result = db.session.execute(
                insert_sql,
                {
                    "user_id": current_user.id,

                    "user_name": current_user.username,

                    "disease_id": disease_id,

                    "confidence": confidence,

                    "monitoring_id": monitoring_id,

                    "selected_symptoms": selected_symptoms,

                    "status": "Completed"
                }
            )


            # ===============================================
            # GET INSERTED ID
            # ===============================================

            diagnosis_ids.append(
                result.lastrowid
            )


        # =====================================================
        # COMMIT
        # =====================================================

        db.session.commit()


        # =====================================================
        # VERY IMPORTANT
        # =====================================================

        return diagnosis_ids


    except Exception as e:

        db.session.rollback()

        logger.exception(
            f"Save Diagnosis History Error: {e}"
        )

        raise
# ---------- DIAGNOSIS INPUT ----------
@admin_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_input():
    # form = DiagnosisForm()
    # # Get all active symptoms
    # symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    # # Make sure IDs are integers
    # form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]
    # if form.validate_on_submit():
    #     # Convert submitted data to integers
    #     selected_ids = [int(s) for s in form.symptoms.data or []]
    #     if not selected_ids:
    #         flash("Please select at least one symptom.", "warning")
    #         return redirect(url_for("admin.diagnosis_input"))
    #     # Store IDs in session
    #     session["selected_symptoms"] = selected_ids
    #     # Store corresponding symptom NAMES for view filtering
    #     selected_symptoms = SymptomsTable.query.filter(SymptomsTable.id.in_(selected_ids)).all()
    #     session["selected_symptoms_names"] = [s.symptom_name for s in selected_symptoms]
    #     return redirect(url_for("admin.diagnosis_result"))
    # return render_template("diagnosis_page/index.html", form=form, user=current_user)
    # try:
    #     form = DiagnosisForm()
    #     # Get all active symptoms
    #     symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    #     # WTForms choices (for validation)
    #     form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]
    
    #     # Group symptoms by type
    #     grouped_symptoms = {
    #         "Grain(គ្រាប់)": [],
    #         "Leaf(ស្លឹក)": [],
    #         "Root(ឬស)": [],
    #         "Stem(ដើម)": []
    #     }
    
    #     for s in symptoms:
    #         if s.symptom_group == "Grain(គ្រាប់)":
    #             grouped_symptoms["Grain(គ្រាប់)"].append(s)
    #         elif s.symptom_group == "Leaf(ស្លឹក)":
    #             grouped_symptoms["Leaf(ស្លឹក)"].append(s)
    #         elif s.symptom_group == "Root(ឬស)":
    #             grouped_symptoms["Root(ឬស)"].append(s)
    #         elif s.symptom_group == "Stem(ដើម)":
    #             grouped_symptoms["Stem(ដើម)"].append(s)
    
    #     #Handle form submit
    #     if form.validate_on_submit():
    #         try:
    #             selected_ids = [int(s) for s in form.symptoms.data or []]
    #             if not selected_ids:
    #                 flash("Please select at least one symptom.", "warning")
    #                 return redirect(url_for("admin.diagnosis_input"))
    #                 # Store in session
    #             session["selected_symptoms"] = selected_ids
    
    #             selected_symptoms = SymptomsTable.query.filter(
    #                 SymptomsTable.id.in_(selected_ids)
    #             ).all()
    
    #             session["selected_symptoms_names"] = [
    #                 s.symptom_name for s in selected_symptoms
    #             ]
    #             return redirect(url_for("admin.diagnosis_result"))
    #         except Exception as form_error:
    #                 flash("Error processing selected symptoms.", "danger")
    #                 print(f"[FORM ERROR]: {form_error}")
    #                 return redirect(url_for("admin.diagnosis_input"))
    #     return render_template(
    #         "diagnosis_page/index.html",
    #         form=form,
    #         grouped_symptoms=grouped_symptoms,
    #         user=current_user
    #     )
    # except Exception as e:
    #     flash("System error: Unable to load diagnosis page.", "danger")
    #     print(f"[DIAGNOSIS ERROR]: {e}")
    #     return redirect(url_for("admin.diagnosis_input"))
    try:
        form = DiagnosisForm()

        # Monitor & Farm params handling
        monitoring_id = request.args.get("monitoring_id", type=int)
        farm_id = request.args.get("farm_id", type=int)

        if monitoring_id:
            session["monitoring_id"] = monitoring_id
        if farm_id:
            session["farm_id"] = farm_id

        # Fetch all active symptoms
        symptoms = SymptomsTable.query.filter_by(is_active=True).all() or []

        # WTForms dynamic choices
        form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

        # Dynamic grouping (handles spacing and unexpected groups)
        grouped_symptoms = {
            "Grain(គ្រាប់)": [],
            "Leaf(ស្លឹក)": [],
            "Root(ឬស)": [],
            "Stem(ដើម)": [],
            "Other(ផ្សេងៗ)": []
        }

        for s in symptoms:
            group = (s.symptom_group or "").strip()
            if group in grouped_symptoms:
                grouped_symptoms[group].append(s)
            else:
                # Fallback for minor string variations or new groups
                grouped_symptoms.setdefault(group if group else "Other(ផ្សេងៗ)", []).append(s)

        # Form submission handling
        if form.validate_on_submit():
            try:
                selected_ids = [int(s) for s in form.symptoms.data or []]

                if not selected_ids:
                    flash("Please select at least one symptom.", "warning")
                    return redirect(url_for("admin.diagnosis_input"))

                session["selected_symptoms"] = selected_ids
                
                selected_symptoms = SymptomsTable.query.filter(
                    SymptomsTable.id.in_(selected_ids)
                ).all()

                session["selected_symptoms_names"] = [
                    s.symptom_name for s in selected_symptoms
                ]

                return redirect(url_for("admin.diagnosis_result"))

            except Exception as form_error:
                flash("Error processing selected symptoms.", "danger")
                print(f"[FORM ERROR]: {form_error}")
                return redirect(url_for("admin.diagnosis_input"))

        return render_template(
            "diagnosis_page/index.html",
            form=form,
            symptoms=symptoms,                  # Added raw symptoms fallback
            grouped_symptoms=grouped_symptoms,  # Dynamic dictionary
            user=current_user,
            monitoring_id=monitoring_id,
            farm_id=farm_id
        )
    except Exception as e:
        flash("System error: Unable to load diagnosis page.", "danger")
        print(f"[DIAGNOSIS ERROR]: {e}")
        return redirect(url_for("admin.dashboard"))
# ---------- DIAGNOSIS RESULT ----------
@admin_bp.route("/diagnosis/result")
@login_required
@role_required("Admin", "Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    #Get selected symptoms
    # selected_ids = session.get("selected_symptoms", [])
    # if not selected_ids:
    #     flash("No symptoms selected.", "warning")
    #     return redirect(url_for("admin.diagnosis_input"))

    # #Run inference
    # conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

    # # SAVE IN SESSION
    # session["rule_trace"] = rule_trace

    # if not conclusions:
    #     flash("No diseases matched your symptoms.", "info")
    #     return redirect(url_for("admin.diagnosis_input"))

    # # Save diagnosis results using raw SQL helper
    # #save_diagnosis_history(conclusions, rule_trace)

    # #Prepare results for template
    # results = []
    # for disease_id, data in conclusions.items():
    #     disease = data["disease"]
    #     results.append({
    #         "disease_id": disease_id,
    #         "disease_name": getattr(disease, "disease_name", ""),
    #         "image": getattr(disease, "image", ""),
    #         "severity_level":  disease.severity_level if disease else None,
    #         "confidence": data.get("certainty", 0.0),
    #         "rules": rule_trace.get(str(disease_id), []),
    #         "explanation": getattr(disease, "explanation", ""),
    #     })

    # # Render result template
    # return render_template(
    #     "diagnosis_page/result.html",
    #     results=results,
    #     user=current_user
    # )
    try:
        # =====================================================
        # GET SELECTED SYMPTOMS
        # =====================================================
        selected_ids = session.get("selected_symptoms",[])
        if not selected_ids:
            flash("No symptoms selected.","warning")
            return redirect(url_for("admin.diagnosis_input"))


        # =====================================================
        # GET MONITORING INFORMATION
        # =====================================================

        monitoring_id = session.get("monitoring_id")
        farm_id = session.get("farm_id")
        # =====================================================
        # RUN INFERENCE
        # =====================================================
        conclusions, rule_trace, skipped_rules = (DiagnosisService.infer(selected_ids))
        # =====================================================
        # SAVE RULE TRACE
        # =====================================================

        session["rule_trace"] = rule_trace
        if not conclusions:
            flash("No diseases matched your symptoms.","info")

            return redirect(url_for("admin.diagnosis_input"))


        # =====================================================
        # SAVE DIAGNOSIS HISTORY
        # =====================================================

        diagnosis_ids = save_diagnosis_history(
            conclusions,
            rule_trace,
            monitoring_id=monitoring_id
        )


        # =====================================================
        # PREPARE RESULTS
        # =====================================================

        results = []

        for index, (disease_id, data) in enumerate(
            conclusions.items()
        ):
            disease = data["disease"]

            # Get corresponding diagnosis ID
            diagnosis_id = (
                diagnosis_ids[index]
                if index < len(diagnosis_ids)
                else None
            )
            certainty = data.get(
                "certainty",
                0.0
            )

            #Get all Treatments
            # treatments = (
            #     DiagnosisService.treatment_disease(
            #         disease_id
            #     )
            # )
            # #Get Best Treatment
            # recommended_treatment = (
            #     DiagnosisService.recommend_treatment(
            #         disease_id
            #     )
            # )
            # #Get Prevention
            # preventions = (
            #     DiagnosisService.prevention_disease(
            #         disease_id
            #     )
            # )
            # =====================================================
            # TREATMENT RECOMMENDATION
            # =====================================================

            recommendation = (
                DiagnosisService.get_treatment_recommendation(
                    disease_id=disease_id,
                    certainty=certainty
                )
            )
            results.append({

                "diagnosis_id": diagnosis_id,

                "disease_id": disease_id,

                "disease_name": (
                    getattr(
                        disease,
                        "disease_name",
                        ""
                    )
                ),

                "image": (
                    getattr(
                        disease,
                        "image",
                        ""
                    )
                ),

                "severity_level": (
                    disease.severity_level
                    if disease
                    else None
                ),

                "confidence": data.get(
                    "certainty",
                    0.0
                ),

                "rules": rule_trace.get(
                    str(disease_id),
                    []
                ),

                "explanation": (
                    getattr(
                        disease,
                        "explanation",
                        ""
                    )
                ),
                # "recommended_treatment": recommended_treatment,
                # "treatments": treatments,
                # "preventions": preventions
                # NEW
                "recommendation": recommendation
            })


        # =====================================================
        # RENDER RESULT
        # =====================================================

        return render_template(
            "diagnosis_page/result.html",

            results=results,

            user=current_user,

            monitoring_id=monitoring_id,

            farm_id=farm_id,

            skipped_rules = skipped_rules
        )


    except Exception as e:

        logger.exception(f"Diagnosis Result Error: {e}")

        flash("Unable to process diagnosis result.","danger")

        return redirect(url_for("admin.diagnosis_input"))

@admin_bp.route("/history")
@login_required
@role_required("Admin", "Expert")
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
        "diagnosis_page/history.html",
        histories=histories,
        page=page,
        total_pages=total_pages
    )
# ---------- DIAGNOSIS EXPLANATION ----------
@admin_bp.route("/diagnosis/explain/<int:diagnosis_id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(diagnosis_id):
    # rule_trace = session.get("rule_trace")
    # if not rule_trace:
    #     flash("Please perform diagnosis first.", "warning")
    #     return redirect(url_for("admin.diagnosis_input"))

    # logs = diagnosis_service.DiagnosisService.explain_disease(disease_id, rule_trace)
    # if not logs:
    #     flash("No explanation available for this disease.", "info")
    #     return redirect(url_for("admin.diagnosis_result"))

    # disease = DiseaseTable.query.get_or_404(disease_id)

    # symptom_ids = session.get("selected_symptoms") or []
    # selected_symptoms = [
    #     s.symptom_name
    #     for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
    # ]

    # #ADD THIS (Calculate confidence)
    # overall_cf = logs[-1]["cf_after"] if logs else 0.0

    # treatments = diagnosis_service.DiagnosisService.treatment_disease(disease_id)
    # preventions = diagnosis_service.DiagnosisService.prevention_disease(disease_id)

    # return render_template(
    #     "diagnosis_page/explain.html",
    #     disease=disease,
    #     logs=logs,
    #     treatments=treatments,
    #     preventions=preventions,
    #     selected_symptoms=selected_symptoms,
    #     certainty=overall_cf,   #PASS TO TEMPLATE
    #     user=current_user
    # )
    try:
        # =====================================================
        # GET DIAGNOSIS HISTORY
        # =====================================================

        diagnosis = (
            DiagnosisHistoryTable.query
            .filter_by(
                id=diagnosis_id,
                user_id=current_user.id
            )
            .first()
        )

        if not diagnosis:

            flash(
                "Diagnosis history is required.",
                "warning"
            )

            return redirect(
                url_for("user.diagnosis_result")
            )


        # =====================================================
        # GET DISEASE
        # =====================================================

        disease = DiseaseTable.query.get_or_404(
            diagnosis.disease_id
        )


        # =====================================================
        # RULE TRACE
        # =====================================================

        rule_trace = session.get("rule_trace")

        if not rule_trace:

            flash(
                "Please perform diagnosis first.",
                "warning"
            )

            return redirect(
                url_for("admin.diagnosis_input")
            )


        # =====================================================
        # EXPLAIN DISEASE
        # =====================================================

        logs = DiagnosisService.explain_disease(
            diagnosis.disease_id,
            rule_trace
        )

        if not logs:

            flash(
                "No explanation available for this disease.",
                "info"
            )

            return redirect(
                url_for("admin.diagnosis_result")
            )


        # =====================================================
        # SELECTED SYMPTOMS
        # =====================================================

        symptom_ids = session.get(
            "selected_symptoms"
        ) or []

        selected_symptoms = []

        if symptom_ids:

            selected_symptoms = [
                s.symptom_name
                for s in SymptomsTable.query.filter(
                    SymptomsTable.id.in_(symptom_ids)
                ).all()
            ]


        # =====================================================
        # CONFIDENCE
        # =====================================================

        overall_cf = (
            logs[-1]["cf_after"]
            if logs
            else 0.0
        )


        # =====================================================
        # TREATMENTS
        # =====================================================

        treatments = (
            DiagnosisService
            .treatment_disease(
                diagnosis.disease_id
            )
        )


        # =====================================================
        # PREVENTIONS
        # =====================================================

        preventions = (
            DiagnosisService
            .prevention_disease(
                diagnosis.disease_id
            )
        )


        # =====================================================
        # RENDER
        # =====================================================

        return render_template(

            "diagnosis_page/explain.html",

            disease=disease,

            diagnosis=diagnosis,

            logs=logs,

            treatments=treatments,

            preventions=preventions,

            selected_symptoms=selected_symptoms,

            certainty=overall_cf,

            user=current_user

        )


    except Exception as e:

        logger.exception(
            f"Diagnosis Explain Error "
            f"(diagnosis_id={diagnosis_id}): {e}"
        )

        flash(
            "Unable to load diagnosis explanation.",
            "danger"
        )

        return redirect(
            url_for("admin.diagnosis_result")
        )
# ---------- TREATMENT & PREVENTION ----------
@admin_bp.route("/diagnosis/treatment/<int:disease_id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("RUN_DIAGNOSIS")
def disease_treatment(disease_id):
    # disease = DiseaseTable.query.get_or_404(disease_id)
    # treatments = service.treatment_disease(disease_id)
    # return render_template(
    #     "diagnosis_page/treatment.html",
    #     disease=disease,
    #     treatments=treatments,
    #     user=current_user
    # )
    try:
        # =====================================================
        # 1. GET DISEASE
        # =====================================================

        disease = DiseaseTable.query.get_or_404(
            disease_id
        )
        # =====================================================
        # 2. GET RECOMMENDED TREATMENT
        # =====================================================

        recommended_treatment = (
            DiagnosisService.recommend_treatment(
                disease_id
            )
        )


        # =====================================================
        # 3. GET ALL TREATMENTS
        # =====================================================

        treatments = (
            DiagnosisService.treatment_disease(
                disease_id
            )
        )


        # =====================================================
        # 4. GET PREVENTIONS
        # =====================================================

        preventions = (
            DiagnosisService.prevention_disease(
                disease_id
            )
        )


        # =====================================================
        # 5. RENDER PAGE
        # =====================================================

        return render_template(

            "diagnosis_page/treatment.html",

            disease=disease,

            recommended_treatment=
                recommended_treatment,

            treatments=treatments,

            preventions=preventions,

            user=current_user

        )


    except Exception as e:

        logger.exception(
            f"Disease Treatment Error: {e}"
        )

        flash(
            "Unable to load treatment information.",
            "danger"
        )

        return redirect(
            url_for("admin.diagnosis_result")
        )
@admin_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@role_required("Admin", "Expert")
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
@admin_bp.route("/diagnosisPrint/<int:disease_id>")
@login_required
@role_required("Admin", "Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_print(disease_id):

    # យកម៉ោងបច្ចុប្បន្នតាម Timezone កម្ពុជា (Asia/Phnom_Penh)
    cambodia_tz = pytz.timezone("Asia/Phnom_Penh")
    current_time = datetime.now(cambodia_tz)
    try:
        # =====================================================
        # 1. GET RULE TRACE
        # =====================================================
        rule_trace = session.get("rule_trace") or {}

        if not rule_trace:
            flash(
                "Please perform diagnosis first.",
                "warning"
            )

            return redirect(
                url_for("admin.diagnosis_input")
            )
        # =====================================================
        # 2. GET DISEASE
        # =====================================================

        disease = DiseaseTable.query.get_or_404(
            disease_id
        )


        # =====================================================
        # 3. GET EXPLANATION LOGS
        # =====================================================

        logs = DiagnosisService.explain_disease(
            disease_id,
            rule_trace
        )

        if not logs:

            flash(
                "No explanation available for this disease.",
                "info"
            )

            return redirect(
                url_for("admin.diagnosis_result")
            )


        # =====================================================
        # 4. GET SELECTED SYMPTOMS
        # =====================================================

        symptom_ids = session.get(
            "selected_symptoms",
            []
        )

        selected_symptoms = []

        if symptom_ids:

            symptoms = (
                SymptomsTable.query
                .filter(
                    SymptomsTable.id.in_(symptom_ids)
                )
                .all()
            )

            selected_symptoms = [
                {
                    "id": symptom.id,
                    "name": symptom.symptom_name
                }
                for symptom in symptoms
            ]


        # =====================================================
        # 5. CERTAINTY
        # =====================================================

        overall_cf = 0.0

        if logs:

            overall_cf = float(
                logs[-1].get(
                    "cf_after",
                    0.0
                )
            )

        # Make sure CF stays between 0 and 1

        overall_cf = max(
            0.0,
            min(
                overall_cf,
                1.0
            )
        )


        # =====================================================
        # 6. CONFIDENCE LEVEL
        # =====================================================

        if overall_cf >= 0.70:

            confidence_level = "High"

            confidence_label = (
                "ទំនុកចិត្តខ្ពស់"
            )

        elif overall_cf >= 0.40:

            confidence_level = "Medium"

            confidence_label = (
                "ទំនុកចិត្តមធ្យម"
            )

        else:

            confidence_level = "Low"

            confidence_label = (
                "ទំនុកចិត្តទាប"
            )


        # =====================================================
        # 7. GET ALL TREATMENTS
        # =====================================================

        treatments = (
            DiagnosisService
            .treatment_disease(
                disease_id
            )
        )


        # =====================================================
        # 8. GET RECOMMENDED TREATMENT
        # =====================================================

        recommended_treatment = None

        if overall_cf >= 0.70:

            recommended_treatment = (
                DiagnosisService
                .recommend_treatment(
                    disease_id
                )
            )


        # =====================================================
        # 9. GET PREVENTIONS
        # =====================================================

        preventions = (
            DiagnosisService
            .prevention_disease(
                disease_id
            )
        )


        # =====================================================
        # 10. RECOMMENDATION MESSAGE
        # =====================================================

        if overall_cf >= 0.70:

            recommendation_message = (
                "ការធ្វើរោគវិនិច្ឆ័យមានទំនុកចិត្តខ្ពស់។ "
                "ប្រព័ន្ធអាចណែនាំវិធីព្យាបាលដែលមាន Priority ខ្ពស់បំផុត។"
            )

        elif overall_cf >= 0.40:

            recommendation_message = (
                "ការធ្វើរោគវិនិច្ឆ័យមានទំនុកចិត្តមធ្យម។ "
                "សូមពិនិត្យរោគសញ្ញាបន្ថែម និងផ្ទៀងផ្ទាត់មុនអនុវត្តការព្យាបាល។"
            )

        else:

            recommendation_message = (
                "ការធ្វើរោគវិនិច្ឆ័យមានទំនុកចិត្តទាប។ "
                "សូមបញ្ចូលរោគសញ្ញាបន្ថែម មុនពេលសម្រេចចិត្តព្យាបាល។"
            )


        # =====================================================
        # 11. RENDER PRINT PAGE
        # =====================================================

        return render_template(

            "diagnosis_page/explain_print.html",

            disease=disease,

            logs=logs,

            treatments=treatments,

            recommended_treatment=(
                recommended_treatment
            ),

            preventions=preventions,

            selected_symptoms=(
                selected_symptoms
            ),

            certainty=overall_cf,

            confidence_level=(
                confidence_level
            ),

            confidence_label=(
                confidence_label
            ),

            recommendation_message=(
                recommendation_message
            ),

            user=current_user,

            now=current_time

        )


    # =========================================================
    # ERROR HANDLING
    # =========================================================

    except Exception as e:

        logger.exception(
            f"Diagnosis Print Error: {e}"
        )

        flash(
            "Failed to generate printable diagnosis. "
            "Try again later.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.diagnosis_result"
            )
        )