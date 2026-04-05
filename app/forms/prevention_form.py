from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from extensions import db
from app.models.diseases import DiseaseTable

PREVENTION_TYPE =[
    ("cultural","cultural"),
    ("Chemical","Chemical"),
    ("Biological","Biological"),
]

def disease_choices():
    return [(d.id, d.disease_name) for d in db.session.scalars(db.select(DiseaseTable).order_by(DiseaseTable.id))]

class PreventionCreateForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    prevention_type = SelectField(
        "Prevention",
        validators=[DataRequired()],
        choices=PREVENTION_TYPE,
        render_kw={"class": "form-control"}
    )
    description = TextAreaField("Description")
    image = FileField("Image", validators=[
        FileRequired("Image is required."),
        FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed.")
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Submit")

class PreventionEditForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    prevention_type = SelectField(
        "Prevention",
        validators=[DataRequired()],
        choices=PREVENTION_TYPE,
        render_kw={"class": "form-control"}
    )
    description = TextAreaField("Description")
    image = FileField("Image", validators=[
        FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed.")
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Update")

class PreventionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Delete")
