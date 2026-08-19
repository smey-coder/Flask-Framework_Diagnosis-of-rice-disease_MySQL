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
from app.models.crop_monitoring import CropMonitoringTable
from app.models.diagnosis_history import DiagnosisHistoryTable
from app.models.diseases import DiseaseTable
from app.models.farm import FarmTable
from app.models.field import FieldTable
from app.models.field_crop import FieldCropTable
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
from app.services.audit_service import log_audit

from app.models.rules import RulesTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.symptoms import SymptomsTable
from app.services.diagnosis_service import DiagnosisService
from app.services.farm_dashboard_service import FarmDashboardService
from app.services.crop_monitoring_service import (CropMonitoringService)
# from app.models.field_crop import FieldCropTable
# from app.models.diagnosis_history import DiagnosisHistoryTable


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

    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    try:

        # =====================================================
        # WEATHER
        # =====================================================

        selected_city_id = request.args.get("city_id")

        if selected_city_id:

            selected_city_weather = WeatherService.get_weather(
                selected_city_id
            )

        if form.validate_on_submit():

            selected_city_name = form.city.data

            if selected_city_name:

                selected_city_weather = WeatherService.get_weather(
                    selected_city_name
                )


        # =====================================================
        # DISEASE
        # =====================================================

        default_disease = DiseaseTable.query.first()


        # =====================================================
        # RECENT DISEASE ACTIVITIES
        # =====================================================

        recent_activities = (
            DiseaseTable.query
            .filter_by(is_active=True)
            .order_by(
                DiseaseTable.created_at.desc()
            )
            .limit(5)
            .all()
        )


        # =====================================================
        # NEW DISEASES
        # =====================================================

        seven_days_ago = (
            datetime.utcnow() - timedelta(days=7)
        )

        new_diseases = (
            DiseaseTable.query
            .filter(
                DiseaseTable.created_at >= seven_days_ago,
                DiseaseTable.is_active == True
            )
            .order_by(
                DiseaseTable.created_at.desc()
            )
            .all()
        )

        new_diseases_count = len(new_diseases)


        # =====================================================
        # FARM MANAGEMENT STATISTICS
        # =====================================================

        farm_statistics = (
            FarmDashboardService.get_statistics(
                user_id=current_user.id
            )
        )


        # =====================================================
        # FIELD CROPS
        # Get only crops belonging to current user
        # =====================================================

        field_crops = (
            db.session.scalars(

                db.select(FieldCropTable)

                .where(

                    FieldCropTable.field.has(

                        FieldCropTable.field.property
                        .mapper.class_.farm.has(

                            user_id=current_user.id

                        )
                    )
                )

                .order_by(
                    FieldCropTable.id.desc()
                )

            ).all()
        )


        # =====================================================
        # CROP STATISTICS
        # =====================================================

        total_field_crops = len(field_crops)


        active_crops = sum(

            1

            for crop in field_crops

            if crop.status in [
                "Active",
                "Growing"
            ]

        )


        growing_crops = sum(

            1

            for crop in field_crops

            if crop.status == "Growing"

        )


        harvested_crops = sum(

            1

            for crop in field_crops

            if crop.status == "Harvested"

        )


        completed_crops = sum(

            1

            for crop in field_crops

            if crop.status == "Completed"

        )


        # =====================================================
        # RECENT CROP MONITORING
        # =====================================================

        recent_monitorings = (
            db.session.scalars(

                db.select(CropMonitoringTable)

                .join(
                    CropMonitoringTable.field_crop
                )

                .where(

                    CropMonitoringTable.field_crop.has(

                        FieldCropTable.field.has(

                            FieldCropTable.field.property
                            .mapper.class_.farm.has(

                                user_id=current_user.id

                            )
                        )
                    )
                )

                .order_by(

                    CropMonitoringTable.monitoring_date.desc(),

                    CropMonitoringTable.id.desc()

                )

                .limit(5)

            ).all()
        )
        # ===================================================== # 9. MONITORING STATISTICS # ===================================================== 
        total_monitorings = len(recent_monitorings) 
        healthy_monitorings = sum( 1 for monitoring in recent_monitorings if monitoring.plant_condition == "Healthy" ) 
        warning_monitorings = sum( 1 for monitoring in recent_monitorings if monitoring.plant_condition in [ "Warning", "Unhealthy" ] ) 
        # ===================================================== # 10. WATER STATUS # ===================================================== 
        good_water_count = sum( 1 for monitoring in recent_monitorings if monitoring.water_status == "Good" ) 
        low_water_count = sum( 1 for monitoring in recent_monitorings if monitoring.water_status == "Low" ) 
        # ===================================================== # 11. PEST STATUS # ===================================================== 
        pest_alert_count = sum( 1 for monitoring in recent_monitorings if monitoring.pest_status not in [ None, "", "None", "Low" ] )
        #===================================================== # 12. DISEASE STATUS # ===================================================== 
        disease_alert_count = sum( 1 for monitoring in recent_monitorings if monitoring.disease_status not in [ None, "", "None", "Low" ] )

        farms = (
            FarmTable.query
            .filter(
                FarmTable.user_id == current_user.id
            )
            .order_by(
                FarmTable.id.desc()
            )
            .all()
        )
        # =====================================================
        # RETURN DASHBOARD
        # =====================================================

        return render_template(

            "user_page/dashboard.html",

            user=current_user,

            farms=farms,

            # Disease
            disease=default_disease,

            recent_activities=recent_activities,

            new_diseases=new_diseases,

            new_diseases_count=new_diseases_count,

            # Weather
            search_results=search_results,

            selected_city_weather=selected_city_weather,

            form=form,

            current_date=current_date,

            # Farm
            farm_statistics=farm_statistics,

            # Field Crops
            field_crops=field_crops,

            total_field_crops=total_field_crops,

            active_crops=active_crops,

            growing_crops=growing_crops,

            harvested_crops=harvested_crops,

            completed_crops=completed_crops,

            # Monitoring
            recent_monitorings=recent_monitorings,
            total_monitorings=total_monitorings, 
            healthy_monitorings=healthy_monitorings, 
            warning_monitorings=warning_monitorings, 
            good_water_count=good_water_count, 
            low_water_count=low_water_count, 
            #Pest / Disease Alerts 
            pest_alert_count=pest_alert_count, 
            disease_alert_count=disease_alert_count

        )


    except Exception as e:

        db.session.rollback()

        print(
            f"Dashboard error: {e}"
        )

        flash(
            "Unable to load dashboard data.",
            "danger"
        )


        # =====================================================
        # DEFAULT FARM STATISTICS
        # =====================================================

        farm_statistics = {

            "total_farms": 0,

            "active_farms": 0,

            "total_fields": 0,

            "active_fields": 0,

            "total_area": 0,

            "total_crops": 0,

            "active_crops": 0,

            "harvested_crops": 0

        }


        return render_template(
            "user_page/dashboard.html",

            user=current_user,

            disease=None,

            recent_activities=[],

            new_diseases=[],

            new_diseases_count=0,

            search_results=search_results,

            selected_city_weather=selected_city_weather,

            form=form,

            current_date=current_date,

            farm_statistics=farm_statistics,

            field_crops=[],

            total_field_crops=0,

            active_crops=0,

            growing_crops=0,

            harvested_crops=0,

            completed_crops=0,

            recent_monitorings=[],
            total_monitorings=0, 
            healthy_monitorings=0, 
            warning_monitorings=0, 
            # Water 
            good_water_count=0, 
            low_water_count=0, 
            # Alerts
            pest_alert_count=0, 
            disease_alert_count=0

        )
@user_bp.route("/farm/<int:farm_id>", methods=["GET"])
@login_required
@role_required("User")
def farm_detail(farm_id):

    try:

        # =====================================================
        # 1. GET FARM
        # =====================================================

        farm = (
            FarmTable.query
            .filter(
                FarmTable.id == farm_id,
                FarmTable.user_id == current_user.id
            )
            .first_or_404()
        )

        # =====================================================
        # 2. GET FIELDS
        # =====================================================

        fields = (
            FieldTable.query
            .filter(
                FieldTable.farm_id == farm.id
            )
            .order_by(
                FieldTable.id.asc()
            )
            .all()
        )

        # =====================================================
        # 3. GET FIELD CROPS
        # =====================================================

        field_crops = (
            FieldCropTable.query
            .join(
                FieldCropTable.field
            )
            .filter(
                FieldTable.farm_id == farm.id
            )
            .order_by(
                FieldCropTable.id.desc()
            )
            .all()
        )

        # =====================================================
        # 4. GET RECENT MONITORINGS
        # =====================================================

        recent_monitorings = (
            CropMonitoringTable.query
            .join(
                CropMonitoringTable.field_crop
            )
            .join(
                FieldCropTable.field
            )
            .filter(
                FieldTable.farm_id == farm.id
            )
            .order_by(
                CropMonitoringTable.monitoring_date.desc(),
                CropMonitoringTable.id.desc()
            )
            .limit(5)
            .all()
        )
        # =====================================================
        # 4.1 GET MONITORING HISTORY
        # =====================================================

        monitoring_history = (
            CropMonitoringTable.query
            .join(
                CropMonitoringTable.field_crop
            )
            .join(
                FieldCropTable.field
            )
            .filter(
                FieldTable.farm_id == farm.id
            )
            .order_by(
                CropMonitoringTable.monitoring_date.desc(),
                CropMonitoringTable.id.desc()
            )
            .all()
        )

        # =====================================================
        # 5. STATISTICS
        # =====================================================

        total_fields = len(fields)

        active_fields = sum(
            1
            for field in fields
            if field.status == "Active"
        )

        total_field_crops = len(field_crops)

        growing_crops = sum(
            1
            for crop in field_crops
            if crop.status == "Growing"
        )

        harvested_crops = sum(
            1
            for crop in field_crops
            if crop.status == "Harvested"
        )

        completed_crops = sum(
            1
            for crop in field_crops
            if crop.status == "Completed"
        )

        # =====================================================
        # 6. MONITORING STATISTICS
        # =====================================================

        total_monitorings = (
            CropMonitoringTable.query
            .join(
                CropMonitoringTable.field_crop
            )
            .join(
                FieldCropTable.field
            )
            .filter(
                FieldTable.farm_id == farm.id
            )
            .count()
        )

        # =====================================================
        # 7. PEST ALERTS
        # =====================================================

        pest_alert_count = sum(
            1
            for monitoring in recent_monitorings
            if monitoring.pest_status
            not in [None, "", "None", "Low"]
        )

        # =====================================================
        # 8. DISEASE ALERTS
        # =====================================================

        disease_alert_count = sum(
            1
            for monitoring in recent_monitorings
            if monitoring.disease_status
            not in [None, "", "None", "Low"]
        )
        # =====================================================
        # MONITORING SUMMARY
        # =====================================================

        monitoring_summary = db.session.execute(
            text("""
                SELECT
                    COUNT(cm.id) AS total_monitorings,

                    SUM(
                        CASE
                            WHEN cm.plant_condition = 'Healthy'
                            THEN 1
                            ELSE 0
                        END
                    ) AS healthy_count,

                    SUM(
                        CASE
                            WHEN cm.plant_condition IN ('Warning', 'Unhealthy')
                            THEN 1
                            ELSE 0
                        END
                    ) AS warning_count

                FROM tbl_crop_monitorings cm

                INNER JOIN tbl_field_crops fc
                    ON fc.id = cm.field_crop_id

                INNER JOIN tbl_fields f
                    ON f.id = fc.field_id

                WHERE f.farm_id = :farm_id
            """),
            {
                "farm_id": farm.id
            }
        ).mappings().first()
        # =====================================================
        # DISEASE COUNT
        # =====================================================

        disease_count = db.session.execute(
            text("""
                SELECT COUNT(DISTINCT dh.id)

                FROM tbl_diagnosis_history dh

                INNER JOIN tbl_crop_monitorings cm
                    ON cm.id = dh.monitoring_id

                INNER JOIN tbl_field_crops fc
                    ON fc.id = cm.field_crop_id

                INNER JOIN tbl_fields f
                    ON f.id = fc.field_id

                WHERE f.farm_id = :farm_id
                AND dh.user_id = :user_id
            """),
            {
                "farm_id": farm.id,
                "user_id": current_user.id
            }
        ).scalar() or 0
        # =====================================================
        # DISEASE ANALYSIS
        # =====================================================

        disease_analysis = db.session.execute(
            text("""
                SELECT
                    dh.disease_id,
                    d.disease_name,
                    COUNT(dh.id) AS detection_count,
                    MAX(dh.created_at) AS last_detected
                FROM tbl_diagnosis_history dh

                INNER JOIN tbl_diseases d
                    ON d.id = dh.disease_id

                INNER JOIN tbl_crop_monitorings cm
                    ON cm.id = dh.monitoring_id

                INNER JOIN tbl_field_crops fc
                    ON fc.id = cm.field_crop_id

                INNER JOIN tbl_fields f
                    ON f.id = fc.field_id

                WHERE f.farm_id = :farm_id
                AND dh.user_id = :user_id

                GROUP BY
                    dh.disease_id,
                    d.disease_name

                ORDER BY
                    detection_count DESC,
                    last_detected DESC
            """),
            {
                "farm_id": farm.id,
                "user_id": current_user.id
            }
        ).mappings().all()
        

        # =====================================================
        # 9. RENDER
        # =====================================================

        return render_template(
            "user_page/farm_detail.html",

            user=current_user,

            # Farm
            farm=farm,

            # Fields
            fields=fields,

            # Field Crops
            field_crops=field_crops,

            # Monitoring
            recent_monitorings=recent_monitorings,

            monitoring_history = monitoring_history,

            # Statistics
            total_fields=total_fields,
            active_fields=active_fields,

            total_field_crops=total_field_crops,

            growing_crops=growing_crops,
            harvested_crops=harvested_crops,
            completed_crops=completed_crops,

            total_monitorings=total_monitorings,

            pest_alert_count=pest_alert_count,
            disease_alert_count=disease_alert_count,

            monitoring_summary=monitoring_summary,

            disease_count=disease_count,

            disease_analysis = disease_analysis
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Farm Detail error: {e}"
        )

        flash(
            "Unable to load farm details.",
            "danger"
        )

        return redirect(
            url_for("user.dashboard")
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
        # =====================================================
        # GET MONITORING INFORMATION
        # =====================================================

        monitoring_id = request.args.get(
            "monitoring_id",
            type=int
        )

        farm_id = request.args.get(
            "farm_id",
            type=int
        )

        # Store monitoring information in session
        if monitoring_id:

            session["monitoring_id"] = monitoring_id

        if farm_id:

            session["farm_id"] = farm_id

        # Get all active symptoms
        symptoms = SymptomsTable.query.filter_by(is_active=True).all()

        # WTForms choices (for validation)
        form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

        # Group symptoms by type
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

        #Handle form submit
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
            user=current_user,
            monitoring_id=monitoring_id,
            farm_id=farm_id
        )
    except Exception as e:
        flash("System error: Unable to load diagnosis page.", "danger")
        print(f"[DIAGNOSIS ERROR]: {e}")
        return redirect(url_for("user.diagnosis_input"))

# @user_bp.route("/save_diagnosis", methods=["POST"])
# @login_required
# def save_diagnosis_history(conclusions, rule_trace=None, monitoring_id=None):
#     """
#     Save diagnosis results to the database using raw SQL.
#     """
#     if not conclusions:
#         return
#     insert_sql = text("""
#         INSERT INTO tbl_diagnosis_history (
#             user_id,
#             user_name,
#             disease_id,
#             confidence,
#             monitoring_id,
#             selected_symptoms,
#             status,
#             created_at
#         )
#         VALUES (
#             :user_id,
#             :user_name,
#             :disease_id,
#             :confidence,
#             :monitoring_id,
#             :selected_symptoms,
#             :status,
#             NOW()
#         )
#     """)

#     # Convert selected symptom IDs to comma-separated string
#     selected_symptoms = ",".join(str(s) for s in session.get("selected_symptoms", []))

#     for disease_id, data in conclusions.items():
#         confidence = data.get("certainty", 0.0)
        
#         db.session.execute(
#             insert_sql,
#             {
#                 "user_id": current_user.id,
#                 "user_name": current_user.username,
#                 "disease_id": disease_id,
#                 "confidence": confidence,
#                 "monitoring_id": monitoring_id,
#                 "selected_symptoms": selected_symptoms,
#                 "status": "Completed"
#             }
#         )

#     db.session.commit()

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


# @user_bp.route("/diagnosis/result")
# @login_required
# @role_required("User")
# @permission_required("RUN_DIAGNOSIS")
# def diagnosis_result():
#     #Get selected symptoms
#     selected_ids = session.get("selected_symptoms", [])
#     if not selected_ids:
#         flash("No symptoms selected.", "warning")
#         return redirect(url_for("user.diagnosis_input"))

#     # =====================================================
#     # GET MONITORING INFORMATION
#     # =====================================================

#     monitoring_id = session.get(
#         "monitoring_id"
#     )

#     farm_id = session.get(
#         "farm_id"
#     )
#     #Run inference
#     conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

#     # SAVE IN SESSION
#     session["rule_trace"] = rule_trace

#     if not conclusions:
#         flash("No diseases matched your symptoms.", "info")
#         return redirect(url_for("user.diagnosis_input"))
    


#     # Save diagnosis results using raw SQL helper
#     save_diagnosis_history(conclusions, rule_trace, monitoring_id=monitoring_id)

#     #Prepare results for template
#     results = []
#     for disease_id, data in conclusions.items():
#         disease = data["disease"]
#         results.append({
#             "disease_id": disease_id,
#             "disease_name": getattr(disease, "disease_name", ""),
#             "image": getattr(disease, "image", ""),
#             "severity_level":  disease.severity_level if disease else None,
#             "confidence": data.get("certainty", 0.0),
#             "rules": rule_trace.get(str(disease_id), []),
#             "explanation": getattr(disease, "explanation", ""),
#         })

#     # Render result template
#     return render_template(
#         "user_page/result.html",
#         results=results,
#         user=current_user,
#         monitoring_id=monitoring_id,
#         farm_id=farm_id
#     )

@user_bp.route("/diagnosis/result")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    try:
        # =====================================================
        # GET SELECTED SYMPTOMS
        # =====================================================
        selected_ids = session.get("selected_symptoms",[])
        if not selected_ids:
            flash("No symptoms selected.","warning")

            return redirect(url_for("user.diagnosis_input"))


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

            return redirect(url_for("user.diagnosis_input"))


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
            "user_page/result.html",

            results=results,

            user=current_user,

            monitoring_id=monitoring_id,

            farm_id=farm_id,

            skipped_rules = skipped_rules
        )


    except Exception as e:

        logger.exception(f"Diagnosis Result Error: {e}")

        flash("Unable to process diagnosis result.","danger")

        return redirect(url_for("user.diagnosis_input"))






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
# @user_bp.route("/diagnosis/explain/<int:diagnosis_id>")
# @login_required
# @role_required("User")
# @permission_required("RUN_DIAGNOSIS")
# def diagnosis_explain(disease_id):
#     try:
#         rule_trace = session.get("rule_trace")
#         if not rule_trace:
#             flash("Please perform diagnosis first.", "warning")
#             return redirect(url_for("user.diagnosis_input"))
        
#         logs = diagnosis_service.explain_disease(disease_id, rule_trace)
#         if not logs:
#             flash("No explanation available for this disease.", "info")
#             return redirect(url_for("user.diagnosis_result"))

#         diagnosis = (
#             DiagnosisHistoryTable.query
#             .filter_by(
#                 disease_id=disease_id,
#                 user_id = current_user.id
#             )
#             .order_by(
#                 DiagnosisHistoryTable.id.desc()
#             )
#             .first()
#         )
#         disease = DiseaseTable.query.get_or_404(disease_id)
        
#         symptom_ids = session.get("selected_symptoms") or []
#         selected_symptoms = [
#             s.symptom_name
#             for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
#         ]
        
#         #ADD THIS (Calculate confidence)
#         overall_cf = logs[-1]["cf_after"] if logs else 0.0
        
#         treatments = diagnosis_service.treatment_disease(disease_id)
#         preventions = diagnosis_service.prevention_disease(disease_id)
        
#         return render_template(
#             "user_page/explain.html",
#             disease=disease,
#             diagnosis=diagnosis,
#             logs=logs,
#             treatments=treatments,
#             preventions=preventions,
#             selected_symptoms=selected_symptoms,
#             certainty=overall_cf,   # ✅ PASS TO TEMPLATE
#             user=current_user
#         )
#     except Exception as e:
#         logger.exception( f"Diagnosis Explain Error " f"(disease_id={disease_id}): {e}" ) 
#         flash( "Unable to load diagnosis explanation.", "danger" ) 
#         return redirect( url_for("user.diagnosis_result") )
# ---------------- DIAGNOSIS EXPLANATION ----------------
@user_bp.route("/diagnosis/explain/<int:diagnosis_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(diagnosis_id):

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
                url_for("user.diagnosis_input")
            )


        # =====================================================
        # EXPLAIN DISEASE
        # =====================================================

        logs = diagnosis_service.explain_disease(
            diagnosis.disease_id,
            rule_trace
        )

        if not logs:

            flash(
                "No explanation available for this disease.",
                "info"
            )

            return redirect(
                url_for("user.diagnosis_result")
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
            diagnosis_service
            .treatment_disease(
                diagnosis.disease_id
            )
        )


        # =====================================================
        # PREVENTIONS
        # =====================================================

        preventions = (
            diagnosis_service
            .prevention_disease(
                diagnosis.disease_id
            )
        )


        # =====================================================
        # RENDER
        # =====================================================

        return render_template(

            "user_page/explain.html",

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
            url_for("user.diagnosis_result")
        )



# ---------------- TREATMENT & PREVENTION ----------------
# @user_bp.route("/diagnosis/treatment/<int:disease_id>")
# @login_required
# @role_required("User")
# @permission_required("RUN_DIAGNOSIS")
# def disease_treatment(disease_id):
#     disease = DiseaseTable.query.get_or_404(disease_id)
#     treatments = diagnosis_service.treatment_disease(disease_id)
#     return render_template("user_page/treatment.html", disease=disease, treatments=treatments, user=current_user)
# ---------------- TREATMENT & PREVENTION ----------------

@user_bp.route(
    "/diagnosis/treatment/<int:disease_id>",
    methods=["GET"]
)
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def disease_treatment(disease_id):

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

            "user_page/treatment.html",

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
            url_for("user.diagnosis_result")
        )

@user_bp.route("/diagnosis/prevention/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def disease_prevention(disease_id):
    disease = DiseaseTable.query.get_or_404(disease_id)
    preventions = diagnosis_service.prevention_disease(disease_id)
    return render_template("user_page/prevention.html", disease=disease, preventions=preventions, user=current_user)

# @user_bp.route("/diagnosisPrint/<int:disease_id>")
# @login_required
# @role_required("User")
# @permission_required("RUN_DIAGNOSIS")
# def diagnosis_print(disease_id):
#     try:
#         rule_trace = session.get("rule_trace")
#         if not rule_trace:
#             flash("Please perform diagnosis first.", "warning")
#             return redirect(url_for("user.diagnosis_input"))

#         logs = diagnosis_service.explain_disease(disease_id, rule_trace)
#         if not logs:
#             flash("No explanation available for this disease.", "info")
#             return redirect(url_for("user.diagnosis_result"))

#         disease = DiseaseTable.query.get_or_404(disease_id)

#         symptom_ids = session.get("selected_symptoms") or []
#         selected_symptoms = [
#             s.symptom_name
#             for s in SymptomsTable.query.filter(SymptomsTable.id.in_(symptom_ids)).all()
#         ]

#         overall_cf = logs[-1]["cf_after"] if logs else 0.0

#         treatments = diagnosis_service.treatment_disease(disease_id)
#         preventions = diagnosis_service.prevention_disease(disease_id)

#         return render_template(
#             "user_page/explain_print.html",
#             disease=disease,
#             logs=logs,
#             treatments=treatments,
#             preventions=preventions,
#             selected_symptoms=selected_symptoms,
#             certainty=overall_cf,
#             user=current_user,
#             now=datetime.now()
#         )

#     except Exception as e:
#         flash("Failed to generate printable diagnosis. Try again later.", "danger")
#         return redirect(url_for("user.diagnosis_explain", disease_id=disease_id))
@user_bp.route("/diagnosisPrint/<int:disease_id>")
@login_required
@role_required("User")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_print(disease_id):
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
                url_for("user.diagnosis_input")
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

        logs = diagnosis_service.explain_disease(
            disease_id,
            rule_trace
        )

        if not logs:

            flash(
                "No explanation available for this disease.",
                "info"
            )

            return redirect(
                url_for("user.diagnosis_result")
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
            diagnosis_service
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
                diagnosis_service
                .recommend_treatment(
                    disease_id
                )
            )


        # =====================================================
        # 9. GET PREVENTIONS
        # =====================================================

        preventions = (
            diagnosis_service
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

            "user_page/explain_print.html",

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

            now=datetime.now()

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
                "user.diagnosis_result"
            )
        )
    
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
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    return render_template('user_page/new_information.html', current_date = current_date)

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

# @user_bp.route("/notifications")
# @login_required
# @role_required("User")
# def get_notifications():

#     user_id = current_user.id

#     results = db.session.query(DiseaseTable).all()

#     data = []

#     for d in results:
#         notif = UserNotification.query.filter_by(
#             user_id=user_id,
#             disease_id=d.id,
#             is_deleted=True
#         ).first()

#         if not notif:
#             data.append({
#                 "id": d.id,
#                 "name": d.disease_name,
#                 "time": d.created_at.isoformat()
#             })

#     return jsonify(data)

# @user_bp.route("/notifications/read/<int:id>", methods=["POST"])
# @login_required
# @role_required("User")
# def read_notification(id):
#     user_id = current_user.id

#     notif = UserNotification.query.filter_by(
#         user_id=user_id,
#         disease_id=id
#     ).first()

#     if not notif:
#         notif = UserNotification(
#             user_id=user_id,
#             disease_id=id,
#             is_read=True
#         )
#         db.session.add(notif)
#     else:
#         notif.is_read = True

#     db.session.commit()
#     return "", 204

# @user_bp.route("/notifications/delete-all", methods=["POST"])
# @login_required
# @role_required("User")
# def delete_all_notifications():
#     try:
#         user_id = current_user.id
#         UserNotification.query.filter_by(user_id=user_id).update({
#             "is_deleted": True
#         })
#         db.session.commit()
#         return "", 204
#     except Exception as e:
#         db.session.rollback()
#         print("[ERROR delete_all_notifications]:", e)
#         return {"error": "Failed to delete"}, 500
    
# @user_bp.route("/notifications/delete/<int:id>", methods=["POST"])
# @login_required
# @role_required("User")
# def delete_notification(id):

#     user_id = current_user.id

#     notif = UserNotification.query.filter_by(
#         user_id=user_id,
#         disease_id=id
#     ).first()

#     if not notif:
#         notif = UserNotification(
#             user_id=user_id,
#             disease_id=id,
#             is_deleted=True
#         )
#         db.session.add(notif)
#     else:
#         notif.is_deleted = True

#     db.session.commit()
#     return "", 204


# =========================================================
# GET ALL NOTIFICATIONS
# =========================================================

# =========================================================
# GET ALL NOTIFICATIONS
# =========================================================

@user_bp.route(
    "/notifications",
    methods=["GET"]
)
@login_required
@role_required("User")
def get_notifications():

    user_id = current_user.id

    try:

        notifications = (
            UserNotification.query
            .filter(
                UserNotification.user_id == user_id,
                UserNotification.is_deleted == False
            )
            .order_by(
                UserNotification.created_at.desc()
            )
            .all()
        )

        data = []

        for notif in notifications:

            # =================================================
            # DISEASE NOTIFICATION
            # =================================================

            if notif.category == "disease":

                disease = DiseaseTable.query.get(
                    notif.disease_id
                )

                if not disease:
                    continue

                data.append({

                    "id": notif.id,

                    "notification_id": notif.id,

                    "category": "disease",

                    "reference_id": disease.id,

                    "title": disease.disease_name,

                    "name": disease.disease_name,

                    "message":
                        "New disease information",

                    "type": "warning",

                    "icon": "bi-virus",

                    "is_read": notif.is_read,

                    "time":
                        notif.created_at.isoformat()
                        if notif.created_at
                        else None
                })


            # =================================================
            # CROP MONITORING NOTIFICATION
            # =================================================

            elif notif.category == "crop_monitoring":

                monitoring = (
                    CropMonitoringTable.query.get(
                        notif.monitoring_id
                    )
                )

                if not monitoring:
                    continue


                # ---------------------------------------------
                # DEFAULT
                # ---------------------------------------------

                notification_type = "info"

                icon = "bi-info-circle"


                # ---------------------------------------------
                # DISEASE
                # ---------------------------------------------

                if monitoring.disease_status in [
                    "Detected",
                    "Severe"
                ]:

                    notification_type = "critical"

                    icon = (
                        "bi-exclamation-triangle-fill"
                    )


                # ---------------------------------------------
                # PEST
                # ---------------------------------------------

                elif monitoring.pest_status in [
                    "Medium",
                    "High"
                ]:

                    notification_type = "warning"

                    icon = "bi-bug-fill"


                # ---------------------------------------------
                # PLANT CONDITION
                # ---------------------------------------------

                elif monitoring.plant_condition in [
                    "Poor",
                    "Critical"
                ]:

                    notification_type = "warning"

                    icon = "bi-heart-pulse-fill"


                # ---------------------------------------------
                # TITLE
                # ---------------------------------------------

                title = "Crop Monitoring Alert"


                # ---------------------------------------------
                # MESSAGE
                # ---------------------------------------------

                message = (
                    f"Plant condition: "
                    f"{monitoring.plant_condition or 'N/A'}"
                )


                # ---------------------------------------------
                # DATA
                # ---------------------------------------------

                data.append({

                    "id": notif.id,

                    "notification_id": notif.id,

                    "category":
                        "crop_monitoring",

                    "reference_id":
                        monitoring.id,

                    "title": title,

                    "name": title,

                    "message": message,

                    "type":
                        notification_type,

                    "icon": icon,

                    "is_read":
                        notif.is_read,

                    "time":
                        notif.created_at.isoformat()
                        if notif.created_at
                        else None
                })


        return jsonify(data), 200


    except Exception as e:

        db.session.rollback()

        print(
            "[ERROR get_notifications]:",
            e
        )

        return jsonify({

            "error":
                "Failed to load notifications."

        }), 500


# =========================================================
# READ NOTIFICATION
# =========================================================

@user_bp.route(
    "/notifications/read/<int:id>",
    methods=["POST"]
)
@login_required
@role_required("User")
def read_notification(id):

    user_id = current_user.id

    try:

        notif = (
            UserNotification.query
            .filter_by(
                id=id,
                user_id=user_id,
                is_deleted=False
            )
            .first()
        )


        if not notif:

            return jsonify({

                "error":
                    "Notification not found."

            }), 404


        notif.is_read = True

        db.session.commit()

        return "", 204


    except Exception as e:

        db.session.rollback()

        print(
            "[ERROR read_notification]:",
            e
        )

        return jsonify({

            "error":
                "Failed to mark notification as read."

        }), 500


# =========================================================
# DELETE ONE NOTIFICATION
# =========================================================

@user_bp.route(
    "/notifications/delete/<int:id>",
    methods=["POST"]
)
@login_required
@role_required("User")
def delete_notification(id):

    user_id = current_user.id

    try:

        notif = (
            UserNotification.query
            .filter_by(
                id=id,
                user_id=user_id
            )
            .first()
        )


        if not notif:

            return jsonify({

                "error":
                    "Notification not found."

            }), 404


        # Soft delete
        notif.is_deleted = True

        db.session.commit()

        return "", 204


    except Exception as e:

        db.session.rollback()

        print(
            "[ERROR delete_notification]:",
            e
        )

        return jsonify({

            "error":
                "Failed to delete notification."

        }), 500


# =========================================================
# DELETE ALL NOTIFICATIONS
# =========================================================

@user_bp.route(
    "/notifications/delete-all",
    methods=["POST"]
)
@login_required
@role_required("User")
def delete_all_notifications():

    user_id = current_user.id

    try:

        (
            UserNotification.query
            .filter_by(
                user_id=user_id,
                is_deleted=False
            )
            .update({

                "is_deleted": True

            })
        )

        db.session.commit()

        return "", 204


    except Exception as e:

        db.session.rollback()

        print(
            "[ERROR delete_all_notifications]:",
            e
        )

        return jsonify({

            "error":
                "Failed to delete notifications."

        }), 500


# =========================================================
# CROP MONITORING DETAIL
# =========================================================

@user_bp.route(
    "/notifications/crop/<int:monitoring_id>",
    methods=["GET"]
)
@login_required
@role_required("User")
def crop_notification_detail(monitoring_id):
    try:
        monitoring = (CropMonitoringService.get_by_id(monitoring_id,current_user.id))
        if not monitoring:

            return jsonify({"error":"Monitoring record not found."}), 404
        
        return jsonify({
            "id": monitoring.id,

            "field_crop_id": monitoring.field_crop_id,
            "field_crop_name": (
                monitoring.field_crop.field.field_name
                if monitoring.field_crop
                else "Unknown"
            ),

            "monitoring_date": (
                monitoring.monitoring_date.isoformat()
                if monitoring.monitoring_date
                else None
            ),

            "growth_stage_id": monitoring.growth_stage_id,
            "growth_stage_name": (
                monitoring.growth_stage.stage_name_kh
                if monitoring.growth_stage
                else "Unknown"
            ),

            "plant_height": (
                float(monitoring.plant_height)
                if monitoring.plant_height is not None
                else None
            ),

            "water_status": monitoring.water_status,

            "plant_condition": monitoring.plant_condition,

            "pest_status": monitoring.pest_status,

            "disease_status": monitoring.disease_status,

            "description": monitoring.description
        }), 200


    except Exception as e:

        db.session.rollback()

        print(
            "[ERROR crop_notification_detail]:",
            e
        )

        return jsonify({

            "error":
                "Failed to load crop monitoring."

        }), 500
    
@user_bp.route("/crop-monitoring/<int:monitoring_id>/detail")
@login_required
@role_required("User")
def crop_monitoring_detail_page(monitoring_id):

    return render_template(
        "user_page/crop_monitorings/crop_monitoring_detail.html",
        monitoring_id=monitoring_id
    )

# @user_bp.route("/monitoring/history", methods=["GET"])
# @login_required
# @role_required("User")
# def monitoring_history():

#     try:

#         # =====================================================
#         # 1. GET MONITORING HISTORY
#         # =====================================================

#         monitorings = (
#             CropMonitoringTable.query

#             # Crop Monitoring
#             .join(
#                 CropMonitoringTable.field_crop
#             )

#             # Field Crop → Field
#             .join(
#                 FieldCropTable.field
#             )

#             # Only current user's farms
#             .join(
#                 FieldTable.farm
#             )

#             .filter(
#                 FarmTable.user_id == current_user.id
#             )

#             .order_by(
#                 CropMonitoringTable.monitoring_date.desc(),
#                 CropMonitoringTable.id.desc()
#             )

#             .all()
#         )


#         # =====================================================
#         # 2. RETURN PAGE
#         # =====================================================

#         return render_template(
#             "user_page/monitoring/history.html",

#             user=current_user,

#             monitorings=monitorings
#         )


#     except Exception as e:

#         db.session.rollback()

#         print(
#             f"Monitoring History error: {e}"
#         )

#         flash(
#             "Unable to load monitoring history.",
#             "danger"
#         )

#         return redirect(
#             url_for("user.dashboard")
#         )

@user_bp.route(
    "/farm/<int:farm_id>/monitoring/<int:monitoring_id>",
    methods=["GET"]
)
@login_required
@role_required("User")
def monitoring_detail(farm_id, monitoring_id):

    try:

        # =====================================================
        # 1. GET FARM
        # =====================================================

        farm = (
            FarmTable.query
            .filter(
                FarmTable.id == farm_id,
                FarmTable.user_id == current_user.id
            )
            .first_or_404()
        )


        # =====================================================
        # 2. GET MONITORING
        # =====================================================

        monitoring = (
            CropMonitoringTable.query

            .join(
                CropMonitoringTable.field_crop
            )

            .join(
                FieldCropTable.field
            )

            .filter(
                CropMonitoringTable.id == monitoring_id,
                FieldTable.farm_id == farm.id
            )

            .first_or_404()
        )


        # =====================================================
        # 3. GET DIAGNOSIS HISTORY
        # =====================================================

        diagnosis_rows = (
            db.session.execute(
                text("""
                    SELECT *
                    FROM tbl_diagnosis_history
                    WHERE monitoring_id = :monitoring_id
                    AND user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {
                    "monitoring_id": monitoring.id,
                    "user_id": current_user.id
                }
            )
            .mappings()
            .all()
        )


        # =====================================================
        # 4. PREPARE DIAGNOSIS DATA
        # =====================================================

        diagnosis_histories = []


        for row in diagnosis_rows:

            # -----------------------------------------------
            # Convert RowMapping to normal dictionary
            # -----------------------------------------------

            diagnosis = dict(row)


            # -----------------------------------------------
            # Get Disease
            # -----------------------------------------------

            disease = (
                DiseaseTable.query
                .filter(
                    DiseaseTable.id == diagnosis["disease_id"]
                )
                .first()
            )

            diagnosis["disease"] = disease


            # -----------------------------------------------
            # Get Selected Symptoms
            # -----------------------------------------------

            symptom_ids = [
                int(x.strip())
                for x in (
                    diagnosis.get("selected_symptoms") or ""
                ).split(",")

                if x.strip().isdigit()
            ]


            # -----------------------------------------------
            # Get Symptoms
            # -----------------------------------------------

            symptoms = []

            if symptom_ids:

                symptoms = (
                    SymptomsTable.query
                    .filter(
                        SymptomsTable.id.in_(symptom_ids)
                    )
                    .all()
                )


            # -----------------------------------------------
            # Create ID → Name
            # -----------------------------------------------

            symptom_map = {
                symptom.id: symptom.symptom_name
                for symptom in symptoms
            }


            # -----------------------------------------------
            # Keep original selected order
            # -----------------------------------------------

            diagnosis["symptom_names"] = [
                symptom_map[symptom_id]
                for symptom_id in symptom_ids
                if symptom_id in symptom_map
            ]


            # -----------------------------------------------
            # Add to list
            # -----------------------------------------------

            diagnosis_histories.append(diagnosis)


        # =====================================================
        # 5. RENDER
        # =====================================================

        return render_template(
            "user_page/monitoring/detail.html",

            user=current_user,

            farm=farm,

            monitoring=monitoring,

            diagnosis_histories=diagnosis_histories
        )


    except Exception as e:

        db.session.rollback()

        print(
            f"Monitoring Detail error: {e}"
        )

        flash(
            "Unable to load monitoring details.",
            "danger"
        )

        return redirect(
            url_for(
                "user.farm_detail",
                farm_id=farm_id
            )
        )

@user_bp.route(
    "/farm/<int:farm_id>/field-crop/<int:field_crop_id>/monitoring-history",
    methods=["GET"]
)
@login_required
@role_required("User")
def monitoring_history(farm_id, field_crop_id):

    try:

        # =====================================================
        # 1. GET FARM
        # =====================================================

        farm = (
            FarmTable.query
            .filter(
                FarmTable.id == farm_id,
                FarmTable.user_id == current_user.id
            )
            .first_or_404()
        )

        # =====================================================
        # 2. GET FIELD CROP
        # =====================================================

        field_crop = (
            FieldCropTable.query
            .join(FieldTable)
            .filter(
                FieldCropTable.id == field_crop_id,
                FieldTable.farm_id == farm.id
            )
            .first_or_404()
        )

        # =====================================================
        # 3. GET MONITORING HISTORY
        # =====================================================

        monitorings = (
            CropMonitoringTable.query
            .filter(
                CropMonitoringTable.field_crop_id == field_crop.id
            )
            .order_by(
                CropMonitoringTable.monitoring_date.desc(),
                CropMonitoringTable.id.desc()
            )
            .all()
        )

        # =====================================================
        # 4. STATISTICS
        # =====================================================

        total_monitorings = len(monitorings)

        healthy_count = sum(
            1
            for monitoring in monitorings
            if monitoring.plant_condition == "Healthy"
        )

        warning_count = sum(
            1
            for monitoring in monitorings
            if monitoring.plant_condition in [
                "Warning",
                "Unhealthy"
            ]
        )

        disease_alert_count = sum(
            1
            for monitoring in monitorings
            if monitoring.disease_status
            not in [None, "", "None", "Low"]
        )

        # =====================================================
        # 5. RENDER
        # =====================================================

        return render_template(
            "user_page/monitoring/history.html",

            user=current_user,

            farm=farm,

            field_crop=field_crop,

            monitorings=monitorings,

            total_monitorings=total_monitorings,

            healthy_count=healthy_count,

            warning_count=warning_count,

            disease_alert_count=disease_alert_count
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"Monitoring History error: {e}"
        )

        flash(
            "Unable to load monitoring history.",
            "danger"
        )

        return redirect(
            url_for(
                "field_crops.index"
            )
        )