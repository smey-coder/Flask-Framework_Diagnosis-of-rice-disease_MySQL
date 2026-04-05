from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class DiseaseTable(UserMixin, db.Model):
    __tablename__ ="tbl_diseases"

    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(200), unique=True, nullable=False)
    disease_type = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity_level = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Disease {self.disease_name}>"