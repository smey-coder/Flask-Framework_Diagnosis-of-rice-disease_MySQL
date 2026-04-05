from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.validators import DataRequired

class DiagnosisForm(FlaskForm):
    symptoms = SelectMultipleField(
        "Select Symptoms",
        coerce=int,
        validators=[DataRequired(message="Please select at least one symptom.")]
    )
    submit = SubmitField("Diagnose")
