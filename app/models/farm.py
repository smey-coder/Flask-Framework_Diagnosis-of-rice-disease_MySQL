from datetime import datetime
from extensions import db
class FarmTable(db.Model):
    __tablename__ = "tbl_farms"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("tbl_users.id"),
        nullable=False
    )

    farm_name = db.Column(
        db.String(150),
        nullable=False
    )
    description = db.Column(
        db.Text,
        nullable=True
    )
    # =========================================================
    # LOCATION
    # =========================================================
    # Example:
    # "Kampong Cham"
    province = db.Column(
        db.String(100),
        nullable=True
    )
    # Example:
    # "Kang Meas"
    district = db.Column(
        db.String(100),
        nullable=True
    )

    # Example:
    # "Kokor"
    commune = db.Column(
        db.String(100),
        nullable=True
    )
    location = db.Column(
        db.String(255),
        nullable=True
    )
     # =========================================================
    # GPS LOCATION
    # =========================================================

    latitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    longitude = db.Column(
        db.Numeric(10, 7),
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

    user = db.relationship(
        "UserTable",
        back_populates="farms"
    )

    fields = db.relationship(
        "FieldTable",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Farm {self.farm_name}>"