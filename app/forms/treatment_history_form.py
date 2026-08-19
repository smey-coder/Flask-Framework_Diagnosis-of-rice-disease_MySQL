from flask_wtf import FlaskForm

from wtforms import (
    DateField,
    SelectField,
    TextAreaField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class TreatmentHistoryForm(FlaskForm):

    # ==========================================
    # TREATMENT DATE
    # ==========================================

    treatment_date = DateField(
        "Treatment Date",
        validators=[
            DataRequired(
                message="Treatment date is required."
            )
        ],
        format="%Y-%m-%d"
    )

    # ==========================================
    # STATUS
    # ==========================================

    status = SelectField(
        "Treatment Status",
        choices=[
            (
                "planned",
                "Planned / គ្រោងទុក"
            ),
            (
                "in_progress",
                "In Progress / កំពុងព្យាបាល"
            ),
            (
                "completed",
                "Completed / បានបញ្ចប់"
            ),
            (
                "failed",
                "Failed / មិនមានប្រសិទ្ធភាព"
            ),
            (
                "cancelled",
                "Cancelled / បានបោះបង់"
            )
        ],
        validators=[
            DataRequired(
                message="Please select treatment status."
            )
        ]
    )

    # ==========================================
    # RESULT
    # ==========================================

    result = TextAreaField(
        "Treatment Result",
        validators=[
            Optional(),
            Length(
                max=1000,
                message="Result must not exceed 1000 characters."
            )
        ],
        render_kw={
            "placeholder":
                "Describe the treatment result..."
        }
    )

    # ==========================================
    # NOTES
    # ==========================================

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),
            Length(
                max=2000,
                message="Notes must not exceed 2000 characters."
            )
        ],
        render_kw={
            "placeholder":
                "Additional treatment notes..."
        }
    )

    # ==========================================
    # SUBMIT
    # ==========================================

    submit = SubmitField(
        "Save Treatment History"
    )

