from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from extensions import db
from app.models.rule_conditions import RuleConditionsTable
from app.models.rules import RulesTable
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
    def paginate(
        page=1,
        per_page=10,
        search=None,
        active_only=None
    ):

        query = RuleConditionsTable.query

        # =====================================
        # SEARCH
        # Condition + Disease + Symptom
        # =====================================

        if search:

            search_pattern = f"%{search}%"

            query = (
                query
                .join(RuleConditionsTable.rule)
                .join(RuleConditionsTable.symptom)
                .join(RulesTable.disease)
                .filter(
                    db.or_(
                        RuleConditionsTable.rule_id.ilike(
                            search_pattern
                        ),

                        DiseaseTable.disease_name.ilike(
                            search_pattern
                        ),

                        SymptomsTable.symptom_name.ilike(
                            search_pattern
                        )
                    )
                )
            )

        # =====================================
        # ACTIVE FILTER
        # =====================================

        if active_only is not None:

            query = query.filter(
                RuleConditionsTable.is_active
                == active_only
            )

        # =====================================
        # ORDER
        # =====================================

        query = query.order_by(
            RuleConditionsTable.id.desc()
        )

        # =====================================
        # PAGINATION
        # =====================================

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    @staticmethod
    def get_by_id(rule_condition_id: int) -> RuleConditionsTable:
        """Get rule condition by ID"""
        rule_condition = RuleConditionsTable.query.get(rule_condition_id)
        if not rule_condition:
            raise ValueError("Rule condition not found.")
        return rule_condition


    # ===================== HELPER FOR FORM DATA =====================
    @staticmethod
    def get_symptoms_grouped_with_diseases():
        """
        ទាញយករោគសញ្ញាទាំងអស់ និង Eager Load យកជំងឺដែលពាក់ព័ន្ធតាមរយៈ Rules
        """
        # Load symptoms ជាមួយ Rule Conditions -> Rules -> Disease
        symptoms = (
            SymptomsTable.query
            .options(
                joinedload(SymptomsTable.rule_conditions)
                .joinedload(RuleConditionsTable.rule)
                .joinedload(RulesTable.disease)
            )
            .order_by(SymptomsTable.symptom_name.asc())
            .all()
        )

        grouped_symptoms = {}
        
        for symptom in symptoms:
            category = getattr(symptom, 'category', 'other') or 'other'
            
            # បង្កើត list ជំងឺដែលទាក់ទងនឹង symptom នេះ (Unique list)
            diseases = []
            seen_disease_ids = set()
            
            for rc in getattr(symptom, 'rule_conditions', []):
                if rc.rule and rc.rule.disease:
                    dis = rc.rule.disease
                    if dis.id not in seen_disease_ids:
                        seen_disease_ids.add(dis.id)
                        diseases.append(dis)
            
            # ភ្ជាប់ list ជំងឺទៅកាន់ symptom object
            symptom.diseases = diseases

            if category not in grouped_symptoms:
                grouped_symptoms[category] = []
                
            grouped_symptoms[category].append(symptom)

        return grouped_symptoms
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
