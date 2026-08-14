from datetime import datetime

from extensions import db


class GrowthStageTable(db.Model):

    __tablename__ = "tbl_growth_stages"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    stage_name_kh = db.Column(
        db.String(150),
        nullable=True
    )
    # =========================================================
    # GROWTH STAGE INFORMATION
    # =========================================================

    stage_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    stage_order = db.Column(
        db.Integer,
        nullable=False
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Active"
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
    # RELATIONSHIP
    # =========================================================

    field_crops = db.relationship(
        "FieldCropTable",
        back_populates="growth_stage"
    )
    monitorings = db.relationship(
        "CropMonitoringTable",
        back_populates="growth_stage"
    )
    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self):

        return (
            f"<GrowthStage "
            f"id={self.id} "
            f"stage_name={self.stage_name} "
            f"stage_order={self.stage_order}>"
        )