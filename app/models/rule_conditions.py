from datetime import datetime
from extensions import db
from app.models.rules import RulesTable
from app.models.symptoms import SymptomsTable


class RuleConditionsTable(db.Model):
    __tablename__ = "tbl_rule_conditions"

    id = db.Column(db.Integer, primary_key=True)

    rule_id = db.Column(db.Integer,db.ForeignKey(RulesTable.id, ondelete="CASCADE"),nullable=False)
    symptom_id = db.Column(db.Integer,db.ForeignKey(SymptomsTable.id, ondelete="CASCADE"),nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # ===================== RELATIONSHIPS =====================
    rule = db.relationship("RulesTable",backref=db.backref("rule_conditions",cascade="all, delete-orphan"))
    symptom = db.relationship("SymptomsTable",backref=db.backref("rule_conditions",cascade="all, delete-orphan"))

    # ===================== CONSTRAINTS =====================
    __table_args__ = (db.UniqueConstraint("rule_id","symptom_id",name="uq_rule_symptom"),)

    def __repr__(self) -> str:
        return f"<RuleCondition id={self.id} rule={self.rule_id} symptom={self.symptom_id}>"
