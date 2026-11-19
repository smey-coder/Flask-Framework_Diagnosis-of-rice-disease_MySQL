import json
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    TextAreaField,
    SelectField,
    HiddenField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
    ValidationError
)

# Rough box around Cambodia (a drawn field must be inside it)
CAMBODIA_LAT = (10.2, 14.9)
CAMBODIA_LNG = (102.2, 107.8)

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

    soil_type = SelectField(
        "ប្រភេទដី / Soil Type",
        choices=[
            ("", "-- ជ្រើសរើសប្រភេទដី --"),
            ("ដីរលោង", "ដីរលោង"),
            ("ដីធម្មតា", "ដីធម្មតា"),
            ("ដីរដុប", "ដីរដុប"),
            ("ដីលិចទឹកជ្រៅ ឬមានទឹកដក់ពេញផ្ទៃ", "ដីលិចទឹកជ្រៅ ឬមានទឹកដក់ពេញផ្ទៃ"),
            ("ដីគ្របដណ្តប់ដោយចំបើង ឬគម្របរុក្ខជាតិ", "ដីគ្របដណ្តប់ដោយចំបើង ឬគម្របរុក្ខជាតិ"),
            ("ដីស្ងួតបែកក្រហែងខ្លាំង ឬមានថ្ម/ក្រួសច្រើន", "ដីស្ងួតបែកក្រហែងខ្លាំង ឬមានថ្ម/ក្រួសច្រើន"),
            ("ផ្សេងៗ", "ផ្សេងៗ")
        ],
        validators=[
            DataRequired(message="សូមជ្រើសរើសប្រភេទដី")
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

    # The shape drawn on the map, saved as GeoJSON text (a Polygon).
    # hidden_tag() renders it; the map script fills it in.
    boundary = HiddenField(
        "ព្រំប្រទល់ស្រែ / Field Boundary",
        validators=[Optional()]
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

    # ---------------------------------------------------------
    # Check the drawn boundary before it is saved
    # ---------------------------------------------------------
    def validate_boundary(self, field):
        raw = (field.data or "").strip()

        if not raw:
            return  # drawing is optional

        if len(raw) > 50000:
            raise ValidationError(
                "ព្រំប្រទល់ស្រែធំពេក (The drawn boundary is too large)."
            )

        try:
            geometry = json.loads(raw)
            ring = geometry["coordinates"][0]

            if geometry.get("type") != "Polygon":
                raise ValueError("not a polygon")

            if len(ring) < 4:          # a closed polygon needs at least 3 corners + the closing point
                raise ValueError("too few points")

            for lng, lat in ring:
                if not (CAMBODIA_LAT[0] <= lat <= CAMBODIA_LAT[1] and
                        CAMBODIA_LNG[0] <= lng <= CAMBODIA_LNG[1]):
                    raise ValueError("outside Cambodia")

        except (ValueError, KeyError, IndexError, TypeError):
            raise ValidationError(
                "ព្រំប្រទល់ស្រែមិនត្រឹមត្រូវ សូមគូរម្តងទៀត (The boundary is not valid, please draw it again)."
            )


class FieldConfirmDeleteForm(FlaskForm):
    submit = SubmitField(
        "លុបចេញ / Delete Field"
    )