from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
    ValidationError
)

from extensions import db
from app.models.farm import FarmTable


# =========================================================
# FARM STATUS
# =========================================================

FARM_STATUS_CHOICES = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
]
# ========================================================= # CAMBODIA PROVINCES # ========================================================= 
CAMBODIA_PROVINCES = [ 
    ("", "Select Province"), 
    ("Banteay Meanchey", "Banteay Meanchey"), 
    ("Battambang", "Battambang"), 
    ("Kampong Cham", "Kampong Cham"), 
    ("Kampong Chhnang", "Kampong Chhnang"), 
    ("Kampong Speu", "Kampong Speu"), 
    ("Kampong Thom", "Kampong Thom"), 
    ("Kampot", "Kampot"), 
    ("Kandal", "Kandal"), 
    ("Kep", "Kep"), 
    ("Koh Kong", "Koh Kong"), 
    ("Kratie", "Kratie"), 
    ("Mondulkiri", "Mondulkiri"), 
    ("Oddar Meanchey", "Oddar Meanchey"), 
    ("Pailin", "Pailin"), 
    ("Phnom Penh", "Phnom Penh"), 
    ("Preah Sihanouk", "Preah Sihanouk"), 
    ("Preah Vihear", "Preah Vihear"), 
    ("Pursat", "Pursat"), 
    ("Prey Veng", "Prey Veng"), 
    ("Ratanakiri", "Ratanakiri"), 
    ("Siem Reap", "Siem Reap"), 
    ("Stung Treng", "Stung Treng"), 
    ("Svay Rieng", "Svay Rieng"), 
    ("Takeo", "Takeo"), 
    ("Tboung Khmum", "Tboung Khmum"), 
 ]

# =========================================================
# FARM CREATE FORM
# =========================================================

class FarmCreateForm(FlaskForm):

    farm_name = StringField(
        "Farm Name",
        validators=[
            DataRequired(
                message="Farm name is required."
            ),
            Length(
                min=2,
                max=150,
                message="Farm name must be between 2 and 150 characters."
            )
        ]
    )
    # ----------------------------------------------------- # PROVINCE # ----------------------------------------------------- 
    province = SelectField( 
        "Province/ខេត្ត", 
        choices=CAMBODIA_PROVINCES, 
        validators=[ DataRequired( message="Please select a province." ) ] ) 
    # ----------------------------------------------------- # DISTRICT # ----------------------------------------------------- 
    district = StringField( 
        "District/ស្រុក", 
        validators=[ 
            DataRequired(
             message="District is required." ), 
             Length( min=2, max=100, message=( "District must be between " "2 and 100 characters." ) ) ] ) 
    # ----------------------------------------------------- # COMMUNE # ----------------------------------------------------- 
    commune = StringField(
        "Commune/ឃុំ", 
        validators=[ 
            DataRequired( message="Commune is required." ), 
            Length( 
                min=2, 
                max=100, 
                message=( "Commune must be between " "2 and 100 characters." ) ) 

        ] )
    
    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=1000,
                message="Description cannot exceed 1000 characters."
            )
        ]
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Location cannot exceed 255 characters."
            )
        ]
    )

    status = SelectField(
            "Status",
            choices=[
                ("Active", "Active"),
                ("Inactive", "Inactive")
            ],
            default="Active",
            validators=[
                DataRequired()
            ]
        )

    submit = SubmitField(
        "Create Farm"
    )


# =========================================================
# FARM EDIT FORM
# =========================================================

class FarmEditForm(FlaskForm):

    farm_name = StringField(
        "Farm Name",
        validators=[
            DataRequired(
                message="Farm name is required."
            ),
            Length(
                min=2,
                max=150,
                message="Farm name must be between 2 and 150 characters."
            )
        ]
    )
    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=1000,
                message="Description cannot exceed 1000 characters."
            )
        ]
    )
    province = SelectField( "Province/ខេត្ត", choices=CAMBODIA_PROVINCES, validators=[ DataRequired( message="Please select a province." ) ] ) 
    district = StringField( "District/ស្រុក", validators=[ DataRequired( message="District is required." ), Length( min=2, max=100, message=( "District must be between " "2 and 100 characters." ) ) ] ) 
    commune = StringField( "Commune/ឃុំ", validators=[ DataRequired( message="Commune is required." ), Length( min=2, max=100, message=( "Commune must be between " "2 and 100 characters." ) ) ] )
    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Location cannot exceed 255 characters."
            )
        ]
    )

    status = SelectField(
        "Status",
        choices=FARM_STATUS_CHOICES,
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Update Farm"
    )


# =========================================================
# FARM DELETE FORM
# =========================================================

class FarmConfirmDeleteForm(FlaskForm):

    submit = SubmitField(
        "Confirm Delete"
    )