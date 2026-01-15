from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class ConsultationTable(UserMixin, db.Model):
    __tablename__ ="tbl_consultations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("tbl_users.id"), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey("tbl_diagnosis_rules.id"), nullable=False)
    consult_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    predicted_disease = db.Column(db.String(200), nullable=False)
    confidence_result = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Consultation {self.id}>"