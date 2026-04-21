from collections import defaultdict
from venv import logger
from flask import Blueprint, abort, current_app, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from app.forms.rule_condition_form import RuleConditionCreateForm, RuleConditionEditForm
from app.forms.rule_form import RuleCreateForm, RuleEditForm
from app.forms.symptom_forms import SymptomCreateForm, SymptomEditForm
from app.models.user import UserTable
from app.services import diagnosis_service
from app.services.rule_condition_service import RuleConditionService
from app.services.rule_service import RuleService
from app.services.symptom_service import SymptomService
from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.decorators.access import role_required, permission_required
from app.models.rule_conditions import RuleConditionsTable
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.forms.user_forms import DeleteAccountForm, UserEditForm, UserProfileForm
from app.forms.diseases_forms import DiseaseCreateForm, DiseaseEditForm, DiseaseSearchForm
from app.forms.diagnosis_form import DiagnosisForm
from app.services.diagnosis_service import DiagnosisService
from app.services.disease_service import DiseaseService

expert_bp = Blueprint(
    "expert", __name__, url_prefix="/expert", template_folder="../../templates"
)
service = DiagnosisService()

def get_grouped_symptoms():
    symptoms = db.session.execute(
        db.select(SymptomsTable).order_by(SymptomsTable.symptom_group)
    ).scalars().all()

    grouped = defaultdict(list)

    for s in symptoms:
        grouped[s.symptom_group].append((s.id, s.symptom_name))

    return grouped

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

@expert_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Expert")
def setting_index():
    form = UserProfileForm(original_user=current_user, obj=current_user)
    return render_template('expert_page/settings.html', form=form, user=current_user)

# ---------------- SETTINGS / PROFILE ----------------
@expert_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_PROFILE")
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
                    return redirect(url_for("expert.setting_index"))

                # must enter old password
                if not old_password:
                    flash("You must enter your old password", "danger")
                    return redirect(url_for("expert.setting_index"))

                # verify old password
                if not check_password_hash(current_user.password_hash, old_password):
                    flash("Old password is incorrect", "danger")
                    return redirect(url_for("expert.setting_index"))

                # update password
                current_user.password_hash = generate_password_hash(new_password)

            # =========================
            # SAVE DATABASE
            # =========================
            db.session.commit()

            flash("Profile updated successfully!", "success")
            return redirect(url_for("expert.setting_index"))

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while updating profile.", "danger")
            print("[ERROR]:", e)

    return render_template(
        "expert_page/settings.html",
        form=form,
        user=current_user
    )

@expert_bp.route("/settings/delete", methods=["POST"])
@login_required
@role_required("Expert")
@permission_required("USER_DELETE_ACCOUNT")
def delete_account():
    form = DeleteAccountForm()
    try:
        if not form.validate_on_submit():
            flash("Invalid request.", "danger")
            return redirect(url_for("expert.setting_index"))
        password = form.password.data.strip()
        
        # get REAL user object from DB (IMPORTANT FIX)
        user = UserTable.query.get(current_user.get_id())

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))

        # check password
        if not check_password_hash(user.password_hash, password):
            flash("Password incorrect. Account not deleted.", "danger")
            return redirect(url_for("expert.setting_index"))

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
        return redirect(url_for("expert.setting_index"))


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
    # Get all active symptoms
    symptoms = SymptomsTable.query.filter_by(is_active=True).all()
    # Make sure IDs are integers
    form.symptoms.choices = [(s.id, s.symptom_name) for s in symptoms]

    if form.validate_on_submit():
        # Convert submitted data to integers
        selected_ids = [int(s) for s in form.symptoms.data or []]

        if not selected_ids:
            flash("Please select at least one symptom.", "warning")
            return redirect(url_for("expert.diagnosis_input"))

        # Store IDs in session
        session["selected_symptoms"] = selected_ids

        # Store corresponding symptom NAMES for view filtering
        selected_symptoms = SymptomsTable.query.filter(SymptomsTable.id.in_(selected_ids)).all()
        session["selected_symptoms_names"] = [s.symptom_name for s in selected_symptoms]

        return redirect(url_for("expert.diagnosis_result"))

    return render_template("expert_page/index.html", form=form, user=current_user)


@expert_bp.route("/diagnosis/result")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_result():
    #Get selected symptoms
    selected_ids = session.get("selected_symptoms", [])
    if not selected_ids:
        flash("No symptoms selected.", "warning")
        return redirect(url_for("expert.diagnosis_input"))

    #Run inference
    conclusions, rule_trace, skipped_rules = DiagnosisService.infer(selected_ids)

    # SAVE IN SESSION
    session["rule_trace"] = rule_trace

    if not conclusions:
        flash("No diseases matched your symptoms.", "info")
        return redirect(url_for("expert.diagnosis_input"))

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
        "expert_page/result.html",
        results=results,
        user=current_user
    )



@expert_bp.route("/diagnosis/explain/<int:disease_id>")
@login_required
@role_required("Expert")
@permission_required("RUN_DIAGNOSIS")
def diagnosis_explain(disease_id):
    rule_trace = session.get("rule_trace")
    if not rule_trace:
        flash("Please perform diagnosis first.", "warning")
        return redirect(url_for("user.diagnosis_input"))

    logs = diagnosis_service.DiagnosisService.explain_disease(disease_id, rule_trace)
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

    treatments = diagnosis_service.DiagnosisService.treatment_disease(disease_id)
    preventions = diagnosis_service.DiagnosisService.prevention_disease(disease_id)

    return render_template(
        "expert_page/explain.html",
        disease=disease,
        logs=logs,
        treatments=treatments,
        preventions=preventions,
        selected_symptoms=selected_symptoms,
        certainty=overall_cf,   # ✅ PASS TO TEMPLATE
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

@expert_bp.route("/create/disease", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("CREATE_DISEASE")
def create_disease():
    form = DiseaseCreateForm()
    if form.validate_on_submit():
        data = {
            "disease_name": form.disease_name.data.strip(),
            "disease_type": form.disease_type.data.strip(),
            "description": form.description.data.strip(),
            "severity_level": form.severity_level.data.strip(),
            "is_active": form.is_active.data
        }

        image_file = form.image.data if form.image.data else None

        try:
            disease = DiseaseService.create_disease(data, image_file)
            flash(f"Disease '{disease.disease_name}' created successfully.", "success")
            return redirect(url_for("expert.index_disease"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("An unexpected error occurred.", "danger")

    return render_template("expert_page/create_disease.html", form=form)

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
            "is_active": form.is_active.data
        }

        image_file = form.image.data if form.image.data else None
        updated = DiseaseService.update_disease(disease_id, data, image_file)
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

@expert_bp.route("/create/create", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("CREATE_SYMPTOM")
def create_symptom():
    form = SymptomCreateForm()
    if form.validate_on_submit():
        data = {
            "symptom_name": form.symptom_name.data,
            "symptom_group": form.symptom_group.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }
        symptom = SymptomService.create_symptom(data)
        flash(f"Symptom '{symptom.symptom_name}' was created successfully.", "success")
        return redirect(url_for("expert.index_symptom"))
    
    return render_template("expert_page/create_symptom.html", form=form)

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

# ================== Rule Condition Management ======================

@expert_bp.route("/rule-condition/")
@login_required
@role_required("Expert")
@permission_required("VIEW_RULE_CONDITION")
def index_rule_condition():
    page = request.args.get("page", 1, type=int)
    active_only = request.args.get("active", default=None, type=int)
    active_only = bool(active_only) if active_only is not None else False

    pagination = RuleConditionService.paginate(
        page=page,
        active_only=active_only
    )

    return render_template(
        "expert_page/rule_condition_pages/index.html",
        rule_conditions=pagination.items,
        pagination=pagination,
        active_only=active_only,
        grouped_symptoms=get_grouped_symptoms()
    )

# ===================== CREATE =====================

@expert_bp.route("/rule-condition/create", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("CREATE_RULE_CONDITION")
def create_rule_condition():
    form = RuleConditionCreateForm()

    if form.validate_on_submit():
        try:
            RuleConditionService.create(form.data)
            flash("Rule condition created successfully.", "success")
            return redirect(url_for("expert.index_rule_condition"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template(
        "expert_page/rule_condition_pages/create.html",
        form=form,
        grouped_symptoms=get_grouped_symptoms()
    )


# ===================== DETAIL =====================

@expert_bp.route("/rule-condition/<int:id>")
@login_required
@role_required("Expert")
@permission_required("VIEW_RULE_CONDITION")
def detail_rule_condition(id):
    rule_condition = RuleConditionService.get_by_id(id)

    if not rule_condition:
        abort(404)

    return render_template(
        "expert_page/rule_condition_pages/detail.html",
        rule_condition=rule_condition,
        grouped_symptoms=get_grouped_symptoms()
    )


# ===================== EDIT =====================

@expert_bp.route("/rule-condition/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_RULE_CONDITION")
def edit_rule_condition(id):
    rule_condition = RuleConditionService.get_by_id(id)

    if not rule_condition:
        abort(404)

    form = RuleConditionEditForm(rule_condition=rule_condition)

    if request.method == "GET":
        form.rule_id.data = rule_condition.rule_id
        form.symptom_id.data = rule_condition.symptom_id
        form.is_active.data = rule_condition.is_active

    if form.validate_on_submit():
        try:
            RuleConditionService.update(rule_condition, form.data)
            flash("Rule condition updated successfully.", "success")
            return redirect(url_for("expert.index_rule_condition"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template(
        "expert_page/rule_condition_pages/edit.html",
        form=form,
        rule_condition=rule_condition,
        grouped_symptoms=get_grouped_symptoms()
    )


# ===================== TOGGLE ACTIVE =====================

@expert_bp.route("/rule-condition/<int:id>/toggle", methods=["POST"])
@login_required
@role_required("Expert")
@permission_required("EDIT_RULE_CONDITION")
def toggle_rule_condition(id):
    rule_condition = RuleConditionService.get_by_id(id)

    if not rule_condition:
        abort(404)

    RuleConditionService.toggle_active(rule_condition)

    flash("Rule condition status updated.", "info")
    return redirect(url_for("expert.index_rule_condition"))