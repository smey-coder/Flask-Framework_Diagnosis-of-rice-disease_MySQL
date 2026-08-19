from datetime import datetime

from extensions import db


class TreatmentHistoryTable(db.Model):
    __tablename__ = "tbl_treatment_histories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # MONITORING
    # ==========================================

    monitoring_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_crop_monitorings.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # ==========================================
    # DIAGNOSIS HISTORY
    # ==========================================

    diagnosis_history_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_diagnosis_history.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # ==========================================
    # TREATMENT
    # ==========================================

    treatment_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_treatments.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    # ==========================================
    # TREATMENT INFORMATION
    # ==========================================

    treatment_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="planned"
    )

    result = db.Column(
        db.String(30),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================
    # TIMESTAMPS
    # ==========================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ==========================================
    # RELATIONSHIPS
    # ==========================================

    monitoring = db.relationship(
        "CropMonitoringTable",
        backref="treatment_histories"
    )

    diagnosis_history = db.relationship(
        "DiagnosisHistoryTable",
        backref="treatment_histories"
    )

    treatment = db.relationship(
        "TreatmentTable",
        backref="treatment_histories"
    )

    def __repr__(self):
        return f"<TreatmentHistory {self.id}>"