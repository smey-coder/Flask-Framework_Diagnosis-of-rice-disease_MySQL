from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from extensions import db
from app.models.symptoms import SymptomsTable

# Symptom severity level choices
SYMPTOM_GROUP =[
    ("Leaf","Leaf"),
    ("Stem","Stem"),
    ("Root","Root"),
    ("Grain","Grain"),
]
class SymptomCreateForm(FlaskForm):
    """Form for creating a new symptom"""
    
    symptom_name = StringField(
        "Symptom Name",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Enter symptom name (e.g., Yellowing, Wilting)"}
    )
    
    symptom_group = SelectField(
        "Symptom Group",
        validators=[DataRequired()],
        choices=SYMPTOM_GROUP,
        render_kw={"class": "form-control"}
    )


    description = TextAreaField(
        "Description",
        validators=[Length(max=1000)],
        render_kw={
            "placeholder": "Describe the symptom in detail",
            "rows": 5
        }
    )
    
    is_active = BooleanField(
        "Active",
        default=True
    )
    
    submit = SubmitField("Save")
    
    def validate_symptom_name(self, field):
        exists = db.session.scalar(
            db.select(SymptomsTable).filter(SymptomsTable.symptom_name == field.data)
        )
        if exists:
            raise ValidationError("This symptom name already exists.")
class SymptomEditForm(FlaskForm):
    """Form for editing an existing symptom"""
    
    symptom_name = StringField(
        "Symptom Name",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Enter symptom name (e.g., Yellowing, Wilting)"}
    )
    
    symptom_group = SelectField(
        "Symptom Group",
        validators=[DataRequired()],
        choices=SYMPTOM_GROUP,
        render_kw={"class": "form-control"}
    )

    
    description = TextAreaField(
        "Description",
        validators=[Length(max=1000)],
        render_kw={
            "placeholder": "Describe the symptom in detail",
            "rows": 5
        }
    )
    is_active = BooleanField(
        "Active",
        default=True
    )
    
    submit = SubmitField("Update Symptom")
    
    def __init__(self, original_symptom: SymptomsTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_symptom = original_symptom
    
    def validate_symptom_name(self, field):
        if field.data != self.original_symptom.symptom_name:
            exists = db.session.scalar(
                db.select(SymptomsTable).filter(SymptomsTable.symptom_name == field.data)
            )
            if exists:
                raise ValidationError("This symptom name already exists.")
class SymptomConfirmDeleteForm(FlaskForm):
    """Form for confirming deletion of a symptom"""
    
    symptom_name = StringField(
        "Symptom Name",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Enter symptom name to confirm deletion"}
    )
    
    submit = SubmitField("Delete Symptom")
    
    def __init__(self, symptom_to_delete: SymptomsTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symptom_to_delete = symptom_to_delete
    
    def validate_symptom_name(self, field):
        if field.data != self.symptom_to_delete.symptom_name:
            raise ValidationError("Symptom name does not match. Deletion cancelled.")
class SymptomSearchForm(FlaskForm):
    """Form for searching symptoms"""
    
    search_query = StringField(
        "Search Symptoms",
        validators=[DataRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Enter symptom name to search"}
    )
    
    submit = SubmitField("Search")
