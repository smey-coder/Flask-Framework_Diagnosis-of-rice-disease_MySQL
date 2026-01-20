from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.diseases import DiseaseTable
class TreatmentTable(UserMixin, db.Model):
    __tablename__ ="tbl_treatments"

    id = db.Column(db.Integer, primary_key=True)
    treatment_type = db.Column(db.String(200), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey(DiseaseTable.id), nullable=False)
    description = db.Column(db.Text, nullable=True)
    method = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Treatment {self.name}>"