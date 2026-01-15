from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.associations import tbl_rule_symptoms

class RuleSymptomTable(UserMixin, db.Model):
    __tablename__ ="tbl_rule_symptoms"

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("tbl_diagnosis_rules.id"), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey("tbl_symptoms.id"), nullable=False)
    # symptom_id = db.relationship("SymptomsTable", secondary=tbl_rule_symptoms, back_populates="rule_symptoms")
    weight_score = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

     
    def __repr__(self) -> str:
        return f"<RuleSymptom {self.id}>"