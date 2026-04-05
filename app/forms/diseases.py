from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from extensions import db
from app.models.diseases import DiseaseTable


# Disease severity level choices
SEVERITY_CHOICES = [
    ("Low(ទាប)", "Low(ទាប)"),
    ("Medium(មធ្យម)", "Medium(មធ្យម)"),
    ("High(ខ្ពស់)", "High(ខ្ពស់)"),
    ("Very high(ខ្ពស់ណាស់)", "Very high(ខ្ពស់ណាស់)"),
]


# Disease type choices
DISEASE_TYPE_CHOICES = [
    ("Fungal(ផ្សិត)", "Fungal(ផ្សិត)"),
    ("Bacterial(បាក់តេរី)", "Bacterial(បាក់តេរី)"),
    ("Viral(មេរោគ)", "Viral(មេរោគ)"),
    ("Nutrient Deficiency(កង្វះសារធាតុចិញ្ចឹំម)", "Nutrient Deficiency(កង្វះសារធាតុចិញ្ចឹំម)"),
    ("Nutrient overload(ការលើសសារធាតុចិញ្ចឹម)", "Nutrient overload(ការលើសសារធាតុចិញ្ចឹម)"),
    ("Poisoning by other substances(ការពុលសារធាតុផ្សេងៗ)", "Poisoning by other substances(ការពុលសារធាតុផ្សេងៗ)"),
]


# ===================== DISEASE CREATE FORM =====================
class DiseaseCreateForm(FlaskForm):
    """Form for creating a new disease"""
    
    disease_name = StringField(
        "Disease Name",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Enter disease name (e.g., Blast, Brown Spot)"}
    )
    
    disease_type = SelectField(
        "Disease Type",
        validators=[DataRequired()],
        choices=DISEASE_TYPE_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    description = TextAreaField(
        "Description",
        validators=[Length(max=1000)],
        render_kw={
            "placeholder": "Describe the disease, symptoms, and conditions",
            "rows": 5
        }
    )
    
    severity_level = SelectField(
        "Severity Level",
        validators=[DataRequired()],
        choices=SEVERITY_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    image = StringField(
        "Image URL",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Path to disease image"}
    )
    
    is_active = BooleanField(
        "Active",
        default=True
    )
    
    submit = SubmitField("Create Disease")
    
    def validate_disease_name(self, field):
        """Ensure disease name is unique"""
        existing = db.session.scalar(
            db.select(DiseaseTable).filter(DiseaseTable.disease_name == field.data)
        )
        if existing:
            raise ValidationError("This disease name already exists.")


# ===================== DISEASE EDIT FORM =====================
class DiseaseEditForm(FlaskForm):
    """Form for editing an existing disease"""
    
    disease_name = StringField(
        "Disease Name",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Enter disease name"}
    )
    
    disease_type = SelectField(
        "Disease Type",
        validators=[DataRequired()],
        choices=DISEASE_TYPE_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    description = TextAreaField(
        "Description",
        validators=[Length(max=1000)],
        render_kw={
            "placeholder": "Describe the disease, symptoms, and conditions",
            "rows": 5
        }
    )
    
    severity_level = SelectField(
        "Severity Level",
        validators=[DataRequired()],
        choices=SEVERITY_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    image = StringField(
        "Image URL",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Path to disease image"}
    )
    
    is_active = BooleanField(
        "Active"
    )
    
    submit = SubmitField("Update Disease")
    
    def __init__(self, original_disease, *args, **kwargs):
        """Initialize form with original disease data"""
        super().__init__(*args, **kwargs)
        self.original_disease = original_disease
        
        # Pre-fill form data on initial load
        if not self.is_submitted():
            self.disease_name.data = original_disease.disease_name
            self.disease_type.data = original_disease.disease_type
            self.description.data = original_disease.description
            self.severity_level.data = original_disease.severity_level
            self.image.data = original_disease.image
            self.is_active.data = original_disease.is_active
    
    def validate_disease_name(self, field):
        """Ensure disease name is unique (except for original)"""
        if field.data == self.original_disease.disease_name:
            return  # Allow same name when editing
        
        existing = db.session.scalar(
            db.select(DiseaseTable).filter(DiseaseTable.disease_name == field.data)
        )
        if existing:
            raise ValidationError("This disease name already exists.")


# ===================== DISEASE CONFIRM DELETE FORM =====================
class DiseaseConfirmDeleteForm(FlaskForm):
    """Form for confirming disease deletion"""
    submit = SubmitField("Confirm Delete")


# ===================== DISEASE SEARCH/FILTER FORM =====================
class DiseaseSearchForm(FlaskForm):
    """Form for searching and filtering diseases"""
    
    disease_name = StringField(
        "Disease Name",
        validators=[Length(max=200)],
        render_kw={"placeholder": "Search by disease name"}
    )
    
    disease_type = SelectField(
        "Disease Type",
        choices=[("", "All Types")] + DISEASE_TYPE_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    severity_level = SelectField(
        "Severity Level",
        choices=[("", "All Levels")] + SEVERITY_CHOICES,
        render_kw={"class": "form-control"}
    )
    
    submit = SubmitField("Search")