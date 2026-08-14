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
            ("", "-- Select Water Status --"),
            ("Good", "Good / ល្អ"),
            ("Low", "Low / ទាប"),
            ("High", "High / ខ្ពស់"),
            ("None", "None / គ្មាន")
        ],
        validators=[
            Optional()
        ]
    )

    # =========================================================
    # PLANT CONDITION
    # =========================================================

    plant_condition = SelectField(
        "Plant Condition",
        choices=[
            ("", "-- Select Plant Condition --"),
            ("Healthy", "Healthy / មានសុខភាពល្អ"),
            ("Moderate", "Moderate / មធ្យម"),
            ("Poor", "Poor / ខ្សោយ"),
            ("Critical", "Critical / ធ្ងន់ធ្ងរ")
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