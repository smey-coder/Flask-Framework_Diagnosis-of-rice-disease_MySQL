from typing import List
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.models.rule_conditions import RuleConditionsTable
from app.services.audit_service import log_audit


class RuleConditionService:
    """
    Service layer for managing Rule ↔ Symptom relationships
    with audit logging
    """

    # ===================== QUERY METHODS =====================
    @staticmethod
    def get_all(active_only: bool = False) -> List[RuleConditionsTable]:
        """Get all rule conditions"""
        query = RuleConditionsTable.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(RuleConditionsTable.id.desc()).all()

    @staticmethod
    def paginate(page: int = 1, per_page: int = 10, active_only: bool = False):
        """Paginated list for admin UI, with optional active_only filter"""
        query = RuleConditionsTable.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(RuleConditionsTable.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_by_id(rule_condition_id: int) -> RuleConditionsTable:
        """Get rule condition by ID"""
        rule_condition = RuleConditionsTable.query.get(rule_condition_id)
        if not rule_condition:
            raise ValueError("Rule condition not found.")
        return rule_condition

    # ===================== CREATE =====================
    @staticmethod
    def create(data: dict) -> RuleConditionsTable:
        """Create new rule condition with audit logging"""
        exists = RuleConditionsTable.query.filter_by(
            rule_id=data["rule_id"],
            symptom_id=data["symptom_id"]
        ).first()
        if exists:
            raise ValueError("This rule condition already exists.")

        rule_condition = RuleConditionsTable(
            rule_id=data["rule_id"],
            symptom_id=data["symptom_id"],
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(rule_condition)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for CREATE
        log_audit(
            "CREATE",
            "rule_conditions",
            rule_condition.id,
            before_data=None,
            after_data={
                "rule_id": rule_condition.rule_id,
                "symptom_id": rule_condition.symptom_id,
                "is_active": rule_condition.is_active
            }
        )

        return rule_condition

    # ===================== UPDATE =====================
    @staticmethod
    def update(rule_condition: RuleConditionsTable, data: dict) -> RuleConditionsTable:
        """Update existing rule condition with audit logging"""
        # Duplicate check
        duplicate = RuleConditionsTable.query.filter(
            RuleConditionsTable.rule_id == data["rule_id"],
            RuleConditionsTable.symptom_id == data["symptom_id"],
            RuleConditionsTable.id != rule_condition.id
        ).first()
        if duplicate:
            raise ValueError("Another rule condition with the same rule and symptom exists.")

        # Before snapshot
        before_data = {
            "rule_id": rule_condition.rule_id,
            "symptom_id": rule_condition.symptom_id,
            "is_active": rule_condition.is_active
        }

        # Update fields
        rule_condition.rule_id = data["rule_id"]
        rule_condition.symptom_id = data["symptom_id"]
        rule_condition.is_active = data.get("is_active", True)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # After snapshot
        after_data = {
            "rule_id": rule_condition.rule_id,
            "symptom_id": rule_condition.symptom_id,
            "is_active": rule_condition.is_active
        }

        # ✅ Audit log for UPDATE
        log_audit("UPDATE", "rule_conditions", rule_condition.id, before_data, after_data)

        return rule_condition

    # ===================== TOGGLE ACTIVE =====================
    @staticmethod
    def toggle_active(rule_condition: RuleConditionsTable) -> RuleConditionsTable:
        """Enable / disable rule condition with audit logging"""
        # Before snapshot
        before_data = {
            "rule_id": rule_condition.rule_id,
            "symptom_id": rule_condition.symptom_id,
            "is_active": rule_condition.is_active
        }

        rule_condition.is_active = not rule_condition.is_active

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Unable to update status: {str(e)}")

        # After snapshot
        after_data = {
            "rule_id": rule_condition.rule_id,
            "symptom_id": rule_condition.symptom_id,
            "is_active": rule_condition.is_active
        }

        # ✅ Audit log for TOGGLE ACTIVE
        log_audit("UPDATE", "rule_conditions", rule_condition.id, before_data, after_data)

        return rule_condition

    # ===================== DELETE =====================
    @staticmethod
    def delete(rule_condition: RuleConditionsTable) -> None:
        """Permanently delete rule condition with audit logging"""
        # Before snapshot
        before_data = {
            "rule_id": rule_condition.rule_id,
            "symptom_id": rule_condition.symptom_id,
            "is_active": rule_condition.is_active
        }

        try:
            db.session.delete(rule_condition)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Unable to delete rule condition: {str(e)}")

        # ✅ Audit log for DELETE
        log_audit("DELETE", "rule_conditions", rule_condition.id, before_data, after_data=None)
