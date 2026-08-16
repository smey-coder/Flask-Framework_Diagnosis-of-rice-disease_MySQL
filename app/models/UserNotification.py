from extensions import db
from datetime import datetime


class UserNotification(db.Model):
    __tablename__ = "user_notification"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("tbl_users.id"),
        nullable=False
    )

    # Disease notification
    disease_id = db.Column(
        db.Integer,
        db.ForeignKey("tbl_diseases.id"),
        nullable=True
    )

    # Crop Monitoring notification
    monitoring_id = db.Column(
        db.Integer,
        db.ForeignKey("tbl_crop_monitorings.id"),
        nullable=True
    )

    # Notification type
    category = db.Column(
        db.String(50),
        nullable=False,
        default="disease"
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )