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
        "វាលស្រែ / Field",
        coerce=int,
        validators=[
            DataRequired(
                message="សូមជ្រើសរើសវាលស្រែ (Please select a field)."
            )
        ]
    )

    rice_variety_id = SelectField(
        "ពូជស្រូវ / Rice Variety",
        coerce=int,
        validators=[
            DataRequired(
                message="សូមជ្រើសរើសពូជស្រូវ (Please select a rice variety)."
            )
        ]
    )

    growth_stage_id = SelectField(
        "វគ្គនៃការលូតលាស់ / Growth Stage",
        coerce=int,
        validators=[
            Optional()
        ]
    )

    planting_date = DateField(
        "ថ្ងៃដាំដុះ / Planting Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="សូមបញ្ចូលថ្ងៃដាំដុះ (Planting date is required)."
            )
        ]
    )

    expected_harvest_date = DateField(
        "ថ្ងៃប្រមូលផលរំពឹងទុក / Expected Harvest Date",
        format="%Y-%m-%d",
        validators=[
            Optional()
        ]
    )

    actual_harvest_date = DateField(
        "ថ្ងៃប្រមូលផលជាក់ស្តែង / Actual Harvest Date",
        format="%Y-%m-%d",
        validators=[
            Optional()
        ]
    )

    area = DecimalField(
        "ផ្ទៃដីដាំដុះ (ហិកតា) / Area (Ha)",
        places=2,
        rounding=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="ផ្ទៃដីមិនអាចតូចជាង ០ បានទេ (Area cannot be negative)."
            )
        ]
    )

    season = SelectField(
        "រដូវដាំដុះ / Season",
        choices=[
            ("Wet Season", "រដូវវស្សា / Wet Season"),
            ("Dry Season", "រដូវប្រាំង / Dry Season")
        ],
        validators=[
            Optional()
        ]
    )

    year = IntegerField(
        "ឆ្នាំ / Year",
        validators=[
            Optional(),
            NumberRange(
                min=2000,
                max=2100,
                message="ឆ្នាំមិនត្រឹមត្រូវ (Invalid year)."
            )
        ]
    )

    status = SelectField(
        "ស្ថានភាព / Status",
        choices=[
            ("Active", "សកម្ម / Active"),
            ("Growing", "កំពុងលូតលាស់ / Growing"),
            ("Completed", "បានបញ្ចប់ / Completed"),
            ("Harvested", "បានប្រមូលផល / Harvested"),
            ("Cancelled", "បានលុបចោល / Cancelled")
        ],
        default="Active",
        validators=[
            DataRequired(
                message="សូមជ្រើសរើសស្ថានភាព (Please select a status)."
            )
        ]
    )

    description = TextAreaField(
        "ការពិពណ៌នាបន្ថែម / Description",
        validators=[
            Optional()
        ]
    )

    submit = SubmitField(
        "រក្សាទុក / Save Field Crop"
    )


class FieldCropDeleteForm(FlaskForm):
    submit = SubmitField(
        "លុបចេញ / Delete Field Crop"
    )