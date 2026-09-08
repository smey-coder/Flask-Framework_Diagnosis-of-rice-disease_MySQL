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
        "ឈ្មោះវាលស្រែ / Field Name",
        validators=[
            DataRequired(
                message="សូមបញ្ចូលឈ្មោះវាលស្រែ (Field name is required)."
            ),
            Length(
                min=2,
                max=150,
                message="ឈ្មោះវាលស្រែត្រូវមានពី ២ ទៅ ១៥០ តួអក្សរ (Field name must be between 2 and 150 characters)."
            )
        ]
    )

    area = DecimalField(
        "ផ្ទៃដី (ហិកតា) / Area (Hectares)",
        places=2,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="ផ្ទៃដីមិនអាចតូចជាង ០ បានទេ (Area cannot be negative)."
            )
        ]
    )

    soil_type = StringField(
        "ប្រភេទដី / Soil Type",
        validators=[
            Optional(),
            Length(
                max=100,
                message="ប្រភេទដីមិនអាចលើសពី ១០០ តួអក្សរបានទេ (Soil type cannot exceed 100 characters)."
            )
        ]
    )

    location = StringField(
        "ទីតាំង / Location",
        validators=[
            Optional(),
            Length(
                max=255,
                message="ទីតាំងមិនអាចលើសពី ២៥៥ តួអក្សរបានទេ (Location cannot exceed 255 characters)."
            )
        ]
    )

    description = TextAreaField(
        "ការពិពណ៌នាបន្ថែម / Description",
        validators=[
            Optional(),
            Length(
                max=1000,
                message="ការពិពណ៌នាមិនអាចលើសពី ១០០០ តួអក្សរបានទេ (Description cannot exceed 1000 characters)."
            )
        ]
    )

    status = SelectField(
        "ស្ថានភាព / Status",
        choices=[
            ("Active", "សកម្ម / Active"),
            ("Inactive", "អសកម្ម / Inactive")
        ],
        default="Active",
        validators=[
            DataRequired(
                message="សូមជ្រើសរើសស្ថានភាព (Please select a status)."
            )
        ]
    )

    submit = SubmitField(
        "រក្សាទុក / Save Field"
    )


class FieldConfirmDeleteForm(FlaskForm):
    submit = SubmitField(
        "លុបចេញ / Delete Field"
    )