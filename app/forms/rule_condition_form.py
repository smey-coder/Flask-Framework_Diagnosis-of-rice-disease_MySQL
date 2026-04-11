from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError
from extensions import db
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.models.rule_conditions import RuleConditionsTable


# ------------------------
# Helper: Rules
# ------------------------
def _rule_choices():
    return [
        (rule.id, f"Rule #{rule.id} - {rule.disease.disease_name}")
        for rule in db.session.scalars(
            db.select(RulesTable).order_by(RulesTable.id)
        )
    ]


# ------------------------
# Helper: Symptoms
# ------------------------
def _symptom_choices():
    return [
        (symptom.id, symptom.symptom_name)
        for symptom in db.session.scalars(
            db.select(SymptomsTable).order_by(SymptomsTable.symptom_name)
        )
    ]


# ------------------------
# Custom Validator
# ------------------------
def validate_symptoms(form, field):
    if not field.data or len(field.data) == 0:
        raise ValidationError("Please select at least one symptom.")


# ========================
# CREATE FORM
# ========================
class RuleConditionCreateForm(FlaskForm):
    rule_id = SelectField(
        "Rule",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"placeholder": "Select Rule"}
    )

    symptom_id = SelectMultipleField(
        "Symptoms",
        coerce=int,
        validators=[validate_symptoms]
    )

    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rule_id.choices = _rule_choices()
        self.symptom_id.choices = _symptom_choices()

        if self.symptom_id.data is None:
            self.symptom_id.data = []


# ========================
# EDIT FORM (GROUP EDIT 🔥)
# ========================
class RuleConditionEditForm(FlaskForm):
    rule_id = SelectField(
        "Rule",
        coerce=int,
        validators=[DataRequired()]
    )

    symptom_id = SelectMultipleField(
        "Symptoms",
        coerce=int,
        validators=[validate_symptoms]
    )

    is_active = BooleanField("Active")
    submit = SubmitField("Update")

    def __init__(self, rule_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rule_id.choices = _rule_choices()
        self.symptom_id.choices = _symptom_choices()

        # 🔥 IMPORTANT: Load ALL symptoms of this rule
        if rule_id and not self.is_submitted():
            conditions = db.session.scalars(
                db.select(RuleConditionsTable).where(
                    RuleConditionsTable.rule_id == rule_id
                )
            ).all()

            self.rule_id.data = rule_id
            self.symptom_id.data = [c.symptom_id for c in conditions]

            # Assume all same status (or just take first)
            if conditions:
                self.is_active.data = conditions[0].is_active


# ========================
# DELETE CONFIRM FORM
# ========================
class RuleConditionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")