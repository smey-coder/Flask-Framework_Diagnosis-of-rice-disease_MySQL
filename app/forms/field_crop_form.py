from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    DateField,
    DecimalField,
    TextAreaField,
    SubmitField,
    IntegerField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange
)


class FieldCropForm(FlaskForm):

    field_id = SelectField(
        "Field",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a field."
            )
        ]
    )

    rice_variety_id = SelectField(
        "Rice Variety",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a rice variety."
            )
        ]
    )

    growth_stage_id = SelectField(
        "Growth Stage",
        coerce=int,
        validators=[
            Optional()
        ]
    )

    planting_date = DateField(
        "Planting Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Planting date is required."
            )
        ]
    )

    expected_harvest_date = DateField(
        "Expected Harvest Date",
        format="%Y-%m-%d",
        validators=[
            Optional()
        ]
    )

    actual_harvest_date = DateField(
        "Actual Harvest Date",
        format="%Y-%m-%d",
        validators=[
            Optional()
        ]
    )

    area = DecimalField(
        "Area",
        places=2,
        rounding=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Area cannot be negative."
            )
        ]
    )
    season = SelectField(
        "Season / រដូវដាំដុះ",
        choices=[
            ("Wet Season", "Wet Season / រដូវវស្សា"),
            ("Dry Season", "Dry Season / រដូវប្រាំង")
        ],
        validators=[
            Optional()
        ]
    )

    year = IntegerField(
        "Year",
        validators=[
            Optional(),
            NumberRange(
                min=2000,
                max=2100,
                message="Invalid year."
            )
        ]
    )

    status = SelectField(
        "Status",
        choices=[
            ("Active", "Active"),
            ("Completed", "Completed"),
            ("Harvested", "Harvested"),
            ("Cancelled", "Cancelled")
        ],
        default="Active",
        validators=[
            DataRequired()
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional()
        ]
    )

    submit = SubmitField(
        "Save Field Crop"
    )


class FieldCropDeleteForm(FlaskForm):

    submit = SubmitField(
        "Delete Field Crop"
    )