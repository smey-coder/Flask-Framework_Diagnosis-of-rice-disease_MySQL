from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from flask import abort

from extensions import db
from app.models.rule_conditions import RuleConditionsTable


class RuleConditionService:
    """
    Service layer for managing Rule ↔ Symptom relationships
    """

    # ===================== QUERY METHODS =====================

    @staticmethod
    def get_all(active_only: bool = False) -> List[RuleConditionsTable]:
        """
        Get all rule conditions
        """
        query = RuleConditionsTable.query

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(RuleConditionsTable.id.desc()).all()

    @staticmethod
    def paginate(page: int = 1, per_page: int = 10):
        """
        Paginated list for admin UI
        """
        return RuleConditionsTable.query.order_by(
            RuleConditionsTable.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(rule_condition_id: int) -> RuleConditionsTable:
        """
        Get rule condition by ID
        """
        return RuleConditionsTable.query.get_or_404(rule_condition_id)

    # ===================== CREATE =====================

    @staticmethod
    def create(data: dict) -> RuleConditionsTable:
        """
        Create new rule condition
        Prevent duplicate rule + symptom
        """
        exists = RuleConditionsTable.query.filter_by(
            rule_id=data["rule_id"],
            symptom_id=data["symptom_id"]
        ).first()

        if exists:
            abort(400, "This rule condition already exists.")

        rule_condition = RuleConditionsTable(
            rule_id=data["rule_id"],
            symptom_id=data["symptom_id"],
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(rule_condition)
            db.session.commit()
            return rule_condition
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, f"Database error: {str(e)}")

    # ===================== UPDATE =====================

    @staticmethod
    def update(
        rule_condition: RuleConditionsTable,
        data: dict
    ) -> RuleConditionsTable:
        """
        Update existing rule condition
        """
        duplicate = RuleConditionsTable.query.filter(
            RuleConditionsTable.rule_id == data["rule_id"],
            RuleConditionsTable.symptom_id == data["symptom_id"],
            RuleConditionsTable.id != rule_condition.id
        ).first()

        if duplicate:
            abort(400, "Another rule condition with the same rule and symptom exists.")

        rule_condition.rule_id = data["rule_id"]
        rule_condition.symptom_id = data["symptom_id"]
        rule_condition.is_active = data.get("is_active", True)

        try:
            db.session.commit()
            return rule_condition
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, f"Database error: {str(e)}")

    # ===================== STATUS =====================

    @staticmethod
    def toggle_active(rule_condition: RuleConditionsTable) -> RuleConditionsTable:
        """
        Enable / disable rule condition
        """
        rule_condition.is_active = not rule_condition.is_active

        try:
            db.session.commit()
            return rule_condition
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, "Unable to update status")

    # ===================== DELETE =====================

    @staticmethod
    def delete(rule_condition: RuleConditionsTable) -> None:
        """
        Permanently delete rule condition
        """
        try:
            db.session.delete(rule_condition)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, "Unable to delete rule condition")
