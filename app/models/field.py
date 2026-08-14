from datetime import datetime
from extensions import db


class FieldTable(db.Model):

    __tablename__ = "tbl_fields"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    farm_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tbl_farms.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    field_name = db.Column(
        db.String(150),
        nullable=False
    )

    area = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    soil_type = db.Column(
        db.String(100),
        nullable=True
    )

    location = db.Column(
        db.String(255),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.Enum(
            "Active",
            "Inactive"
        ),
        nullable=False,
        default="Active"
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

    # =====================================================
    # RELATIONSHIP
    # =====================================================

    farm = db.relationship(
        "FarmTable",
        back_populates="fields"
    )
    field_crops = db.relationship(
        "FieldCropTable",
        back_populates="field",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Field {self.field_name}>"