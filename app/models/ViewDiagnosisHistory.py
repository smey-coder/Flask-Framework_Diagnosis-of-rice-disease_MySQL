from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ViewDiagnosisHistory(db.Model):
    __tablename__ = 'view_diagnosis_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    full_name = db.Column(db.String(80), nullable=False)
    disease_name = db.Column(db.String(200), nullable=False)
    disease_type = db.Column(db.String(200), nullable=False)
    severity_level = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    confidence = db.Column(db.Float, nullable=False)