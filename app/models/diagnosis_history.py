from extensions import db
from datetime import datetime
from app.models.diseases import DiseaseTable
from app.models.user import UserTable  # Assuming you have a UserTable

class DiagnosisHistoryTable(db.Model):
    __tablename__ = 'tbl_diagnosis_history'

    id = db.Column(db.Integer, primary_key=True)

    # Information about the user performing the diagnosis
    user_id = db.Column(db.Integer, db.ForeignKey('tbl_users.id'), nullable=True)  # FK to users
    user_name = db.Column(db.String(100), default="Guest")

    # Disease diagnosed (FK to tbl_diseases)
    disease_id = db.Column(db.Integer, db.ForeignKey('tbl_diseases.id'), nullable=False)

    # Selected symptoms stored as JSON
    selected_symptoms = db.Column(db.Text, nullable=True)  # store list of symptom IDs or names

    # Confidence score
    confidence = db.Column(db.Float, nullable=False)

    # Additional optional notes
    notes = db.Column(db.Text, nullable=True)

    # Status and timestamps
    status = db.Column(db.String(50), default='Completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    disease = db.relationship('DiseaseTable', backref='histories')
    user = db.relationship('UserTable', backref='diagnosis_histories')

    def set_symptoms(self, symptoms: list):
        """Store selected symptoms as JSON string"""
        import json
        self.selected_symptoms = json.dumps(symptoms)

    def get_symptoms(self) -> list:
        """Retrieve symptoms as Python list"""
        import json
        return json.loads(self.selected_symptoms or "[]")

    def __repr__(self):
        return f"<DiagnosisHistory {self.id} - User {self.user_name} - Disease {self.disease_id}>"
