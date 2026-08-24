from extensions import db
from datetime import datetime
from app.models.diseases import DiseaseTable
from app.models.user import UserTable  # Assuming you have a UserTable
import json

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

    monitoring_id = db.Column(
            db.Integer,
            db.ForeignKey(
                "tbl_crop_monitorings.id",
                ondelete="SET NULL"
            ),
            nullable=True
    )
    # Status and timestamps
    status = db.Column(db.String(50), default='Completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    disease = db.relationship('DiseaseTable', backref='histories')
    user = db.relationship('UserTable', backref='diagnosis_histories')

    monitoring = db.relationship(
        "CropMonitoringTable",
        back_populates="diagnosis_histories"
    )

    def set_symptoms(self, symptoms: list):
        """Store selected symptoms as JSON string"""
        import json
        if isinstance(symptoms, list):
            self.selected_symptoms = json.dumps(symptoms)
        else:
            self.selected_symptoms = json.dumps([symptoms])

    def get_symptoms(self) -> list:
        """Retrieve symptoms as Python list safely without raising JSONDecodeError"""
        if not self.selected_symptoms:
            return []
        # If already a list or tuple object
        if isinstance(self.selected_symptoms, (list, tuple)):
            return list(self.selected_symptoms)

        # If stored as a single int/float
        if isinstance(self.selected_symptoms, (int, float)):
            return [int(self.selected_symptoms)]

        val_str = str(self.selected_symptoms).strip()

        # Attempt standard JSON decoding
        try:
            data = json.loads(val_str)
            if isinstance(data, list):
                return data
            elif isinstance(data, (int, str)):
                return [data]
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback 1: Handle comma-separated strings (e.g., "1, 2, 3")
        if "," in val_str:
            return [item.strip() for item in val_str.split(",") if item.strip()]

        # Fallback 2: Plain string single ID (e.g., "1")
        return [val_str]

    def __repr__(self):
        return f"<DiagnosisHistory {self.id} - User {self.user_name} - Disease {self.disease_id}>"
