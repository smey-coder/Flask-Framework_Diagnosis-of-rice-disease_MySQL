from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from extensions import db
from app.models.diseases import DiseaseTable

TREATMENT_TYPE = [
    ("Cultural / វិធានការកសិកម្ម", "Cultural / វិធានការកសិកម្ម"),
    ("Chemical / វិធានការប្រើសារធាតុគីមី", "Chemical / វិធានការប្រើសារធាតុគីមី"),
    ("Biological / វិធានការជីវសាស្ត្រ", "Biological / វិធានការជីវសាស្ត្រ"),
    ("Physical / វិធានការរូបវន្ត", "Physical / វិធានការរូបវន្ត"),
    ("Preventive / វិធានការបង្កា", "Preventive / វិធានការបង្ការ"),
    ("Integrated / ការគ្រប់គ្រងចម្រុះ", "Integrated / ការគ្រប់គ្រងចម្រុះ"),
]

def disease_choices():
    return [(d.id, d.disease_name) for d in db.session.scalars(db.select(DiseaseTable).order_by(DiseaseTable.id))]

class TreatmentCreateForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    treatment_type = SelectField(
        "Treatment",
        validators=[DataRequired()],
        choices=TREATMENT_TYPE,
        render_kw={"class": "form-control"}
    )
    description = TextAreaField("Description")
    method = StringField(
        "Method",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Short description (Optional)"},
    )
    image = FileField("Image", validators=[
        FileRequired("Image is required."),
        FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed.")
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Submit")

class TreatmentEditForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    treatment_type = SelectField(
        "Prevention",
        validators=[DataRequired()],
        choices=TREATMENT_TYPE,
        render_kw={"class": "form-control"}
    )
    description = TextAreaField("Description")
    method = StringField(
        "Description",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Short description (Optional)"},
    )
    image = FileField("Image", validators=[
        FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed.")
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Update")

class TreatmentConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Delete")
