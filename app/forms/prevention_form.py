from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SubmitField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from extensions import db
from app.models.diseases import DiseaseTable

PREVENTION_TYPE = [
    ("Cultural / វិធានការកសិកម្ម", "Cultural / វិធានការកសិកម្ម"),
    ("Chemical / វិធានការប្រើសារធាតុគីមី", "Chemical / វិធានការប្រើសារធាតុគីមី"),
    ("Biological / វិធានការជីវសាស្ត្រ", "Biological / វិធានការជីវសាស្ត្រ"),
    ("Physical / វិធានការរូបវន្ត", "Physical / វិធានការរូបវន្ត"),
    ("Preventive / វិធានការបង្កា", "Preventive / វិធានការបង្ការ"),
    ("Integrated / ការគ្រប់គ្រងចម្រុះ", "Integrated / ការគ្រប់គ្រងចម្រុះ"),
]

def disease_choices():
    return [(d.id, d.disease_name) for d in db.session.scalars(db.select(DiseaseTable).order_by(DiseaseTable.id))]

class PreventionCreateForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    prevention_type = SelectField(
        "Prevention Type",
        validators=[DataRequired()],
        choices=PREVENTION_TYPE,
        render_kw={"class": "form-control"}
    )
    method = StringField(
            "Method",
            validators=[Length(max=255)],
            render_kw={"placeholder": "Short description (Optional)"},
    )
    description = TextAreaField("Description")
    priority = IntegerField(
            "Prioirty/អទិភាព",
            validators=[
                DataRequired(),
                NumberRange(
                    min=1,
                    max=10,
                    message="Priority must be between 1 and 10."
                )
            ],
            default=1,
            render_kw={
                "class": "form-control",
                "min": 1,
                "max": 10,
                "placeholder" : "1 = Highest recommendation"
            }
        )
    image = FileField("Image", validators=[
        FileRequired("Image is required."),
        FileAllowed(["jpg", "jpeg", "png", "webp"], 
                    
                    "Only images are allowed."
        )
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Submit")

class PreventionEditForm(FlaskForm):
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    prevention_type = SelectField(
        "Prevention Type",
        validators=[DataRequired()],
        choices=PREVENTION_TYPE,
        render_kw={"class": "form-control"}
    )
    method = StringField(
            "Method",
            validators=[Length(max=255)],
            render_kw={"placeholder": "Short description (Optional)"},
    )
    description = TextAreaField("Description")
    priority = IntegerField(
            "Prioirty/អទិភាព",
            validators=[
                DataRequired(),
                NumberRange(
                    min=1,
                    max=10,
                    message="Priority must be between 1 and 10."
                )
            ],
            default=1,
            render_kw={
                "class": "form-control",
                "min": 1,
                "max": 10,
                "placeholder" : "1 = Highest recommendation"
            }
    )
    image = FileField("Image", validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], 
                        "Only images are allowed."
            )
    ])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Update")

class PreventionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Delete")
