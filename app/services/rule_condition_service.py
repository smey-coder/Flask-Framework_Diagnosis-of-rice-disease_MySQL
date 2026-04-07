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
    def create(data: dict):
        try:
            rule_id = data.get("rule_id")
            symptom_ids = data.get("symptom_id")

            if not rule_id or not symptom_ids:
                raise ValueError("rule_id and symptom_id are required.")

            # ✅ Ensure list
            if not isinstance(symptom_ids, list):
                symptom_ids = [symptom_ids]

            created_items = []

            # ✅ Get existing in ONE query (fast)
            existing = RuleConditionsTable.query.filter(
                RuleConditionsTable.rule_id == rule_id,
                RuleConditionsTable.symptom_id.in_(symptom_ids)
            ).all()

            existing_ids = {e.symptom_id for e in existing}

            for sid in symptom_ids:
                if sid in existing_ids:
                    continue

                rule_condition = RuleConditionsTable(
                    rule_id=rule_id,
                    symptom_id=sid,
                    is_active=data.get("is_active", True)
                )

                db.session.add(rule_condition)
                created_items.append(rule_condition)

            if not created_items:
                raise ValueError("Rule conditions already exist.")

            db.session.commit()

            # ✅ Audit log
            for item in created_items:
                log_audit(
                    "CREATE",
                    "rule_conditions",
                    item.id,
                    before_data=None,
                    after_data={
                        "rule_id": item.rule_id,
                        "symptom_id": item.symptom_id,
                        "is_active": item.is_active
                    }
                )

            return created_items

        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error: {str(e)}")

    # ===================== UPDATE =====================
    @staticmethod
    def update(rule_condition: RuleConditionsTable, data: dict):
        try:
            rule_id = data.get("rule_id")
            symptom_ids = data.get("symptom_id")

            if not rule_id or not symptom_ids:
                raise ValueError("rule_id and symptom_id are required.")

            # ✅ Normalize to list
            if not isinstance(symptom_ids, list):
                symptom_ids = [symptom_ids]

            updated_items = []

            for sid in symptom_ids:
                # ✅ Check duplicate (exclude current record)
                duplicate = RuleConditionsTable.query.filter(
                    RuleConditionsTable.rule_id == rule_id,
                    RuleConditionsTable.symptom_id == sid,
                    RuleConditionsTable.id != rule_condition.id
                ).first()

                if duplicate:
                    continue  # or raise error if strict

                # Before snapshot
                before_data = {
                    "rule_id": rule_condition.rule_id,
                    "symptom_id": rule_condition.symptom_id,
                    "is_active": rule_condition.is_active
                }

                # Update
                rule_condition.rule_id = rule_id
                rule_condition.symptom_id = sid
                rule_condition.is_active = data.get("is_active", True)

                updated_items.append((rule_condition, before_data))

            if not updated_items:
                raise ValueError("No valid updates (duplicates found).")

            db.session.commit()

            # ✅ Audit log
            for item, before_data in updated_items:
                log_audit(
                    "UPDATE",
                    "rule_conditions",
                    item.id,
                    before_data,
                    {
                        "rule_id": item.rule_id,
                        "symptom_id": item.symptom_id,
                        "is_active": item.is_active
                    }
                )

            return [item for item, _ in updated_items]

        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error: {str(e)}")

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
