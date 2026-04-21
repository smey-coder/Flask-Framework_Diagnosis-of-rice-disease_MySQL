from datetime import datetime, timedelta
import json
from venv import logger
from flask import Blueprint, abort, jsonify, render_template, redirect, request, session, url_for, flash
from flask_login import login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

from app import services
from app.decorators.access import role_required, permission_required
from app.forms.diagnosis_form import DiagnosisForm
from app.forms.diseases_forms import DiseaseSearchForm
from app.forms.user_forms import DeleteAccountForm, UserEditForm, UserProfileForm
from app.forms.weather_form import CitySearchForm
from app.models.UserNotification import UserNotification
from app.models.diagnosis_history import DiagnosisHistoryTable
from app.models.diseases import DiseaseTable
from app.models.role import RoleTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.rules import RulesTable
from app.models.symptoms import SymptomsTable
from app.models.user import UserTable
from app.services.disease_service import DiseaseService
from app.services.user_service import UserService
from app.services.weather_service import WeatherService
from extensions import db
from app.services.diagnosis_service import DiagnosisService
from app.services.rule_service import RuleService
from app.services.rule_condition_service import RuleConditionService
from app.services.user_service import UserService

from app.models.rules import RulesTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.symptoms import SymptomsTable
from app.services.diagnosis_service import DiagnosisService

# Create user blueprint
user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="../../templates")
diagnosis_service = DiagnosisService()

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

# ---------------- DASHBOARD ----------------
@user_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
@role_required("User")
def dashboard():
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

    # Default disease to display
    default_disease = DiseaseTable.query.first()  # or choose a specific one

    # Recent activities (last 5 active diseases)
    recent_activities = DiseaseTable.query \
        .filter_by(is_active=True) \
        .order_by(DiseaseTable.created_at.desc()) \
        .limit(5) \
        .all()

    # New diseases for notifications (added in last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_diseases = DiseaseTable.query \
        .filter(DiseaseTable.created_at >= seven_days_ago, DiseaseTable.is_active==True) \
        .order_by(DiseaseTable.created_at.desc()) \
        .all()
    
    new_diseases_count = len(new_diseases)

    return render_template(
        "user_page/dashboard.html", 
        user=current_user,
        disease=default_disease,
        recent_activities=recent_activities,
        new_diseases=new_diseases,
        new_diseases_count=new_diseases_count,
        search_results=search_results,
        selected_city_weather=selected_city_weather,
        form=form
    )

# ---------------- SETTINGS ----------------
@user_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("User")
def setting_index():
    form = UserProfileForm(original_user=current_user, obj=current_user)
    return render_template('user_page/settings.html', form=form, user=current_user )

@user_bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
@role_required("User")
def edit_profile():
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
                    return redirect(url_for("user.edit_profile"))

                # must enter old password
                if not old_password:
                    flash("You must enter your old password", "danger")
                    return redirect(url_for("user.edit_profile"))

                # verify old password
                if not check_password_hash(current_user.password_hash, old_password):
                    flash("Old password is incorrect", "danger")
                    return redirect(url_for("user.edit_profile"))

                # update password
                current_user.password_hash = generate_password_hash(new_password)

            # =========================
            # SAVE DATABASE
            # =========================
            db.session.commit()

            flash("Profile updated successfully!", "success")
            return redirect(url_for("user.setting_index"))

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while updating profile.", "danger")
            print("[ERROR]:", e)

    return render_template(
        "user_page/settings.html",
        form=form,
        user=current_user
    )
from werkzeug.security import check_password_hash

@user_bp.route("/settings/delete", methods=["POST"])
@login_required
@role_required("User")
@permission_required("USER_DELETE_ACCOUNT")
def delete_account():
    form = DeleteAccountForm()
    try:
        if not form.validate_on_submit():
            flash("Invalid request.", "danger")
            return redirect(url_for("user.setting_index"))

        password = form.password.data.strip()

        # get REAL user object from DB (IMPORTANT FIX)
        user = UserTable.query.get(current_user.get_id())

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))

        # check password
        if not check_password_hash(user.password_hash, password):
            flash("Password incorrect. Account not deleted.", "danger")
            return redirect(url_for("user.setting_index"))

        # delete user safely
        db.session.delete(user)
        db.session.commit()

        logout_user()

        flash("Your account has been deleted successfully.", "success")
        return redirect(url_for("auth.login"))

    except Exception as e:
        db.session.rollback()
        print("[ERROR delete_account]:", e)
        flash("Failed to delete account. Try again later.", "danger")
        return redirect(url_for("user.setting_index"))

# ---------------- ABOUT ----------------
@user_bp.route("/about")
@login_required
@role_required("User")
@permission_required("USER_ABOUT")
def about():
    about_info = {
        "app_name": "Rice disease diagnostic system",
        "version": "1.0.0",
        "type_app": "Expert System(AI)",
        "developer": "San Reaksmey, Try Reaksmey, Pen Panhna, Tath Kongea",
        "email": "sanreaksmey01@gmail.com",
        "description": "Helps farmers diagnose rice diseases and manage treatments efficiently.",
    }
    return render_template("user_page/about.html", about=about_info)
# @user_bp.route("/change-password", methods=["POST"])
# @login_required
# def change_password():
#     form = ChangePasswordForm()

#     if form.validate_on_submit():
#         if check_password_hash(current_user.password_hash, form.old_password.data):
#             current_user.password_hash = generate_password_hash(form.password.data)
#             db.session.commit()
#             flash("Password updated successfully", "success")
#         else:
#             flash("Old password is incorrect", "danger")

#     return redirect(url_for("user.setting_index"))
# ---------------- DIAGNOSIS ----------------
@user_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_input():
    try:
        form = DiagnosisForm()

        # ✅ Get all active symptoms
        symptoms = SymptomsTable.query.filter_by(is_active=True).all()

        # WTForms choices (for validation)
        form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

        # ✅ Group symptoms by type
        grouped_symptoms = {
            "Grain(គ្រាប់)": [],
            "Leaf(ស្លឹក)": [],
            "Root(ឬស)": [],
            "Stem(ដើម)": []
        }

        for s in symptoms:
            if s.symptom_group == "Grain(គ្រាប់)":
                grouped_symptoms["Grain(គ្រាប់)"].append(s)
            elif s.symptom_group == "Leaf(ស្លឹក)":
                grouped_symptoms["Leaf(ស្លឹក)"].append(s)
            elif s.symptom_group == "Root(ឬស)":
                grouped_symptoms["Root(ឬស)"].append(s)
            elif s.symptom_group == "Stem(ដើម)":
                grouped_symptoms["Stem(ដើម)"].append(s)

        # ✅ Handle form submit
        if form.validate_on_submit():
            try:
                selected_ids = [int(s) for s in form.symptoms.data or []]

                if not selected_ids:
                    flash("Please select at least one symptom.", "warning")
                    return redirect(url_for("user.diagnosis_input"))

                # Store in session
                session["selected_symptoms"] = selected_ids

                selected_symptoms = SymptomsTable.query.filter(
                    SymptomsTable.id.in_(selected_ids)
                ).all()

                session["selected_symptoms_names"] = [
                    s.symptom_name for s in selected_symptoms
                ]

                return redirect(url_for("user.diagnosis_result"))

            except Exception as form_error:
                flash("Error processing selected symptoms.", "danger")
                print(f"[FORM ERROR]: {form_error}")
                return redirect(url_for("user.diagnosis_input"))

        return render_template(
            "user_page/index.html",
            form=form,
            grouped_symptoms=grouped_symptoms,
            user=current_user
        )
    except Exception as e:
        flash("System error: Unable to load diagnosis page.", "danger")
        print(f"[DIAGNOSIS ERROR]: {e}")
        return redirect(url_for("user.diagnosis_input"))

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

@user_bp.route("/diagnosisPrint/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_print(disease_id):
    try:
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

        overall_cf = logs[-1]["cf_after"] if logs else 0.0

        treatments = diagnosis_service.treatment_disease(disease_id)
        preventions = diagnosis_service.prevention_disease(disease_id)

        return render_template(
            "user_page/explain_print.html",
            disease=disease,
            logs=logs,
            treatments=treatments,
            preventions=preventions,
            selected_symptoms=selected_symptoms,
            certainty=overall_cf,
            user=current_user,
            now=datetime.now()
        )

    except Exception as e:
        flash("Failed to generate printable diagnosis. Try again later.", "danger")
        return redirect(url_for("user.diagnosis_explain", disease_id=disease_id))
    
@user_bp.route("/diseases/show")
@login_required
@role_required("User")
def disease_index():
    """List all diseases with search functionality"""
    try:
        page = request.args.get("page", 1, type=int)
        search_form = DiseaseSearchForm(request.args, meta={"csrf_enabled": False})
        
        disease_name = request.args.get("disease_name", "").strip()
        disease_type = request.args.get("disease_type", "").strip()
        severity_level = request.args.get("severity_level", "").strip()
        
        diseases = DiseaseService.search_diseases(
            disease_name=disease_name if disease_name else None,
            disease_type=disease_type if disease_type else None,
            severity_level=severity_level if severity_level else None,
            page=page,
            per_page=10
        )
        
        return render_template(
            "user_page/disease_index.html",
            diseases=diseases,
            search_form=search_form,
            current_user=current_user
        )
    except Exception as e:
        logger.error(f"Error listing diseases: {e}")
        flash("An error occurred while loading diseases.", "danger")
        return redirect(url_for("user.dashboard"))

@user_bp.route("/information")
@login_required
@role_required("User")
def new_information():
    return render_template('user_page/new_information.html')

@user_bp.route("/information/<int:id>")
@login_required
@role_required("User")
def disease_detail(id):
    disease = DiseaseTable.query.get_or_404(id)

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    new_diseases = DiseaseTable.query.filter(
        DiseaseTable.created_at >= seven_days_ago,
        DiseaseTable.is_active == True
    ).order_by(DiseaseTable.created_at.desc()).all()

    new_diseases_count = len(new_diseases)

    return render_template(
        "user_page/disease_detail.html",
        disease=disease,
        new_diseases=new_diseases,
        new_diseases_count=new_diseases_count
    )

@user_bp.route("/notifications")
@login_required
@role_required("User")
def get_notifications():

    user_id = current_user.id

    results = db.session.query(DiseaseTable).all()

    data = []

    for d in results:
        notif = UserNotification.query.filter_by(
            user_id=user_id,
            disease_id=d.id,
            is_deleted=True
        ).first()

        if not notif:
            data.append({
                "id": d.id,
                "name": d.disease_name,
                "time": d.created_at.isoformat()
            })

    return jsonify(data)

@user_bp.route("/notifications/read/<int:id>", methods=["POST"])
@login_required
@role_required("User")
def read_notification(id):
    user_id = current_user.id

    notif = UserNotification.query.filter_by(
        user_id=user_id,
        disease_id=id
    ).first()

    if not notif:
        notif = UserNotification(
            user_id=user_id,
            disease_id=id,
            is_read=True
        )
        db.session.add(notif)
    else:
        notif.is_read = True

    db.session.commit()
    return "", 204

@user_bp.route("/notifications/delete-all", methods=["POST"])
@login_required
@role_required("User")
def delete_all_notifications():
    try:
        user_id = current_user.id
        UserNotification.query.filter_by(user_id=user_id).update({
            "is_deleted": True
        })
        db.session.commit()
        return "", 204
    except Exception as e:
        db.session.rollback()
        print("[ERROR delete_all_notifications]:", e)
        return {"error": "Failed to delete"}, 500
    
@user_bp.route("/notifications/delete/<int:id>", methods=["POST"])
@login_required
@role_required("User")
def delete_notification(id):

    user_id = current_user.id

    notif = UserNotification.query.filter_by(
        user_id=user_id,
        disease_id=id
    ).first()

    if not notif:
        notif = UserNotification(
            user_id=user_id,
            disease_id=id,
            is_deleted=True
        )
        db.session.add(notif)
    else:
        notif.is_deleted = True

    db.session.commit()
    return "", 204
