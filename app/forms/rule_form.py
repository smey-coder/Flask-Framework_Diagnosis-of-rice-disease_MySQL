from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField,
    FileField
)
from wtforms.validators import DataRequired, Optional, NumberRange

from app.models.diseases import DiseaseTable
from extensions import db


# ========================= HELPERS =========================

def disease_choices():
    """Return disease choices for select field"""
    return [
        (d.id, f"Disease #{d.id} - {d.disease_name}")
        for d in db.session.scalars(
            db.select(DiseaseTable).order_by(DiseaseTable.id)
        )
    ]


# ========================= CREATE FORM =========================

class RuleCreateForm(FlaskForm):
    disease_id = SelectField(
        "Disease",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )

    certainty = FloatField(
        "Certainty Factor (CF)",
        validators=[
            DataRequired(),
            NumberRange(min=-1.0, max=1.0)
        ],
        render_kw={
            "step": "0.01",
            "placeholder": "e.g. 0.8"
        }
    )

    explanation = TextAreaField(
        "Explanation",
        validators=[Optional()],
        render_kw={
            "rows": 3,
            "placeholder": "Explain rule reasoning"
        }
    )
    is_active = BooleanField(
        "Active",
        default=True
    )

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disease_id.choices = disease_choices()


# ========================= EDIT FORM =========================

class RuleEditForm(FlaskForm):
    disease_id = SelectField(
        "Disease",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )

    certainty = FloatField(
        "Certainty Factor (CF)",
        validators=[
            DataRequired(),
            NumberRange(min=-1.0, max=1.0)
        ],
        render_kw={"step": "0.01"}
    )

    explanation = TextAreaField(
        "Explanation",
        validators=[Optional()],
        render_kw={"rows": 3}
    )


    is_active = BooleanField(
        "Active"
    )

    submit = SubmitField("Update")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disease_id.choices = disease_choices()


# ========================= DELETE CONFIRM =========================

class RuleConfirmDelete(FlaskForm):
    submit = SubmitField("Confirm Delete")
