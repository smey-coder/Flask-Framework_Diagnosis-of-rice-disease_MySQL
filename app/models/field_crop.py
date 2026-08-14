from datetime import datetime
from extensions import db

class FieldCropTable(db.Model):
    __tablename__ = "tbl_field_crops"
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

    field_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_fields.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    rice_variety_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_rice_varieties.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    # Current growth stage
    growth_stage_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_growth_stages.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # =========================================================
    # CROP INFORMATION
    # =========================================================

    planting_date = db.Column(
        db.Date,
        nullable=False
    )

    expected_harvest_date = db.Column(
        db.Date,
        nullable=True
    )

    actual_harvest_date = db.Column(
        db.Date,
        nullable=True
    )

    area = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    season = db.Column(
        db.String(50),
        nullable=True
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Growing"
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

    field = db.relationship(
        "FieldTable",
        back_populates="field_crops"
    )

    rice_variety = db.relationship(
        "RiceVarietyTable",
        back_populates="field_crops"
    )

    growth_stage = db.relationship(
        "GrowthStageTable",
        back_populates="field_crops"
    )
    monitorings = db.relationship(
        "CropMonitoringTable",
        back_populates="field_crop",
        cascade="all, delete-orphan"
    )
    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self):

        return (
            f"<FieldCrop "
            f"id={self.id} "
            f"field_id={self.field_id} "
            f"rice_variety_id={self.rice_variety_id}>"
        )