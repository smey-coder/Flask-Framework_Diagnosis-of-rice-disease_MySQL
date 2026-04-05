from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class SymptomsTable(UserMixin, db.Model):
    __tablename__ ="tbl_symptoms"

    id = db.Column(db.Integer, primary_key=True)
    symptom_name = db.Column(db.String(200), unique=True, nullable=False)
    symptom_group = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Symptoms {self.symptom_name}>"