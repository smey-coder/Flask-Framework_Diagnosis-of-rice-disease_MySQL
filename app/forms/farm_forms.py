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