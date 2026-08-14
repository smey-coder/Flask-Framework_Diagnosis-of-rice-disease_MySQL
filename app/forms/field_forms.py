from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    DecimalField,
    TextAreaField,
    SelectField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange
)


class FieldForm(FlaskForm):
    field_name = StringField(
        "Field Name",
        validators=[
            DataRequired(
                message="Field name is required."
            ),
            Length(
                min=2,
                max=150
            )
        ]
    )

    area = DecimalField(
        "Area (hectares)",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Area cannot be negative."
            )
        ],
        places=2
    )

    soil_type = StringField(
        "Soil Type",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=1000)
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
        "Save Field"
    )


class FieldConfirmDeleteForm(FlaskForm):

    submit = SubmitField(
        "Delete Field"
    )