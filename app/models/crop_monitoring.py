from datetime import datetime

from extensions import db


class CropMonitoringTable(db.Model):

    __tablename__ = "tbl_crop_monitorings"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================
    # FOREIGN KEYS
    # =========================================================

    field_crop_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_field_crops.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    growth_stage_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_growth_stages.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # =========================================================
    # MONITORING INFORMATION
    # =========================================================

    monitoring_date = db.Column(
        db.Date,
        nullable=False
    )

    plant_height = db.Column(
        db.Numeric(6, 2),
        nullable=True
    )

    water_status = db.Column(
        db.String(30),
        nullable=True
    )

    plant_condition = db.Column(
        db.String(50),
        nullable=True
    )

    pest_status = db.Column(
        db.String(50),
        nullable=True
    )

    disease_status = db.Column(
        db.String(50),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

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

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    field_crop = db.relationship(
        "FieldCropTable",
        back_populates="monitorings"
    )

    growth_stage = db.relationship(
        "GrowthStageTable",
        back_populates="monitorings"
    )

    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self):

        return (
            f"<CropMonitoring "
            f"id={self.id} "
            f"field_crop_id={self.field_crop_id} "
            f"monitoring_date={self.monitoring_date}>"
        )