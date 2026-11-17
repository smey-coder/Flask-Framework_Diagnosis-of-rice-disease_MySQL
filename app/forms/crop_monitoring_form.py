from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    DateField,
    DecimalField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange
)


class CropMonitoringForm(FlaskForm):

    # =========================================================
    # FIELD CROP
    # =========================================================

    field_crop_id = SelectField(
        "Field Crop",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a field crop."
            )
        ]
    )

    # =========================================================
    # MONITORING DATE
    # =========================================================

    monitoring_date = DateField(
        "Monitoring Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Monitoring date is required."
            )
        ]
    )

    # =========================================================
    # GROWTH STAGE
    # =========================================================
    growth_stage_id = SelectField(
        "Growth Stage",
        coerce=int,
        validators=[
            Optional()
        ]
    )

    # =========================================================
    # PLANT HEIGHT
    # =========================================================

    plant_height = DecimalField(
        "Plant Height",
        places=2,
        rounding=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Plant height cannot be negative."
            )
        ]
    )

    # =========================================================
    # WATER STATUS
    # =========================================================

    water_status = SelectField(
        "Water Status",
        choices=[
            ("", "-- ជ្រើសរើសស្ថានភាពទឹក --"),
            ("Always wet មានទឹកជាប់លាប់ (ទឹកគ្របដណ្តប់ដីបានល្អ)",   "មានទឹកជាប់លាប់ (ទឹកគ្របដណ្តប់ដីបានល្អ)"),
            ("Mostly moist សើមភាគច្រើន (ដីសើម តែស្ងួតម្តងម្កាល)", "សើមភាគច្រើន (ដីសើម តែស្ងួតម្តងម្កាល)"),
            ("Often dry ស្ងួតញឹកញាប់ (ដីស្ងួត)",    "ស្ងួតញឹកញាប់ (ដីស្ងួត)"),
            ("Very dry ស្ងួតខ្លាំង / ប្រេះ (ដីរឹង និងប្រេះ)",     "ស្ងួតខ្លាំង / ប្រេះ (ដីរឹង និងប្រេះ)"),
        ],
        validators=[DataRequired(message="សូមជ្រើសរើសស្ថានភាពទឹក")]
    )

    # =========================================================
    # PLANT CONDITION
    # =========================================================

    plant_condition = SelectField(
        "Rice Situation",
        # choices=[
        #     ("", "-- Select Plant Condition --"),
        #     ("Healthy", "Healthy / មានសុខភាពល្អ"),
        #     ("Moderate", "Moderate / មធ្យម"),
        #     ("Poor", "Poor / ខ្សោយ"),
        #     ("Critical", "Critical / ធ្ងន់ធ្ងរ")
        # ],
        choices=[
                ("", "-- Select Rice Situation --"),
                ("Very good","Very good - ល្អណាស់"),
                ("Good", "Good - ល្អ"),
                ("Moderate","Moderate - មធ្យម"),
                ("Not Good","Not Good - មិនល្អ")
        ],
        validators=[
            Optional()
        ]
    )

    # =========================================================
    # PEST STATUS
    # =========================================================

    pest_status = SelectField(
        "Pest Status",
        choices=[
            ("", "-- Select Pest Status --"),
            ("None", "None / គ្មាន"),
            ("Low", "Low / តិច"),
            ("Medium", "Medium / មធ្យម"),
            ("High", "High / ច្រើន")
        ],
        validators=[
            Optional()
        ]
    )

    # =========================================================
    # DISEASE STATUS
    # =========================================================

    disease_status = SelectField(
        "Disease Status",
        choices=[
            ("", "-- Select Disease Status --"),
            ("None", "None / គ្មាន"),
            ("Suspected", "Suspected / សង្ស័យ"),
            ("Detected", "Detected / រកឃើញ"),
            ("Severe", "Severe / ធ្ងន់ធ្ងរ")
        ],
        validators=[
            Optional()
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
    # SUBMIT
    # =========================================================

    submit = SubmitField(
        "Save Monitoring"
    )


# =============================================================
# DELETE FORM
# =============================================================

class CropMonitoringDeleteForm(FlaskForm):

    submit = SubmitField(
        "Delete Monitoring"
    )