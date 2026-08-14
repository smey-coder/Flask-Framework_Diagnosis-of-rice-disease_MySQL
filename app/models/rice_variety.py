from datetime import datetime
from extensions import db


class RiceVarietyTable(db.Model):
    __tablename__ = "tbl_rice_varieties"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    variety_name = db.Column(
            db.String(150),
            nullable=False
    )

    name_kh = db.Column(
            db.String(150),
            nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )


    status = db.Column(
        db.String(20),
        default="Active",
        nullable=False
    )

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

    field_crops = db.relationship(
        "FieldCropTable",
        back_populates="rice_variety"
    )
   

    def __repr__(self) -> str:
        return f"<RiceVariety {self.name_kh}>"