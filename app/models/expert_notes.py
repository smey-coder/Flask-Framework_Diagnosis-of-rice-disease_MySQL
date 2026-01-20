from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.diseases import DiseaseTable
from app.models.rules import RulesTable
from app.models.user import UserTable

class ExpertNoteTable(UserMixin, db.Model):
    __tablename__ ="tbl_expert_notes"

    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey(DiseaseTable.id), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey(RulesTable.id), nullable=False)
    note_content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserTable.id), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Active")  # e.g., pending, approved, rejected

    def __repr__(self) -> str:
        return f"<ExpertNote {self.id}>"