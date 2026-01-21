from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from extensions import db
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable


def _rule_choices():
    return [
        (rule.id, f"Rule #{rule.id} - Disease {rule.disease_id}")
        for rule in db.session.scalars(
            db.select(RulesTable).order_by(RulesTable.id)
        )
    ]


def _symptom_choices():
    return [
        (symptom.id, symptom.symptom_name)
        for symptom in db.session.scalars(
            db.select(SymptomsTable).order_by(SymptomsTable.symptom_name)
        )
    ]


class RuleConditionCreateForm(FlaskForm):
    rule_id = SelectField("Rule", coerce=int, validators=[DataRequired()], render_kw={"placeholder": "Select Rule ID"})
    symptom_id = SelectField("Symptom", coerce=int, validators=[DataRequired()], render_kw={"placeholder": "Select Symptom ID"})
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rule_id.choices = _rule_choices()
        self.symptom_id.choices = _symptom_choices()


class RuleConditionEditForm(FlaskForm):
    rule_id = SelectField("Rule", coerce=int, validators=[DataRequired()])
    symptom_id = SelectField("Symptom", coerce=int, validators=[DataRequired()])
    is_active = BooleanField("Active")
    submit = SubmitField("Update")

    def __init__(self, rule_condition, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rule_id.choices = _rule_choices()
        self.symptom_id.choices = _symptom_choices()

        if not self.is_submitted():
            self.rule_id.data = rule_condition.rule_id
            self.symptom_id.data = rule_condition.symptom_id
            self.is_active.data = rule_condition.is_active


class RuleConditionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
