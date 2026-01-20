from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.rules import RulesTable
from app.models.symptoms import SymptomsTable

class RuleConditionsTable(UserMixin, db.Model):
    __tablename__ ="tbl_rule_conditions"

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey(RulesTable.id), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey(SymptomsTable.id), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<RuleConditions {self.id} - Rule {self.rule_id}>"