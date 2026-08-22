from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
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


GROWTH_STAGE_STATUS_CHOICES = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
]


class RiceVarietyForm(FlaskForm):

    # =========================================================
    # STAGE NAME
    # =========================================================
    variety_name = StringField(
        "English Name",
        validators=[
            DataRequired(
                message="English name is required."
            ),
            Length(
                min=2,
                max=150,
                message="English name cannot exceed 150 characters."
            )
        ]
    )

    # =========================================================
    # KHMER NAME
    # =========================================================

    name_kh = StringField(
        "Khmer Name",
        validators=[
            # Optional(),
            DataRequired(message="Khmer name is required."),
            Length(
                min=2,
                max=150,
                message="Khmer name cannot exceed 150 characters."
            )
        ]
    )

    # =========================================================
    # DESCRIPTION
    # =========================================================

    description = TextAreaField(
        "Description",
        validators=[
            Optional()
        ]
    )

    # =========================================================
    # STAGE ORDER
    # =========================================================

    growth_duration_days = IntegerField(
        "Growth Duration Days",
        validators=[
            DataRequired(
                message="Growth Duration Day is required."
            ),
            NumberRange(
                min=1,
                max=500,
                message="Growth Duration Day must be between 1 and 100."
            )
        ]
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = SelectField(
        "Status",
        choices=GROWTH_STAGE_STATUS_CHOICES,
        validators=[
            DataRequired(
                message="Status is required."
            )
        ]
    )

    # =========================================================
    # SUBMIT
    # =========================================================

    submit = SubmitField(
        "Save Growth Stage"
    )
class DeleteConfirmForm(FlaskForm):

    submit = SubmitField("Yes, Delete")