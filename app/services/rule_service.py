from typing import List
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.models.rules import RulesTable
from app.services.audit_service import log_audit


class RuleService:
    """Service layer for Rule business logic with audit logging."""

    @staticmethod
    def get_all_rules(active_only: bool = False):
        query = db.session.query(RulesTable).options(joinedload(RulesTable.disease))
        if active_only:
            query = query.filter(RulesTable.is_active.is_(True))
        return query.order_by(RulesTable.id.desc()).all()

    @staticmethod
    def get_rule_by_id(rule_id: int):
        return (
            db.session.query(RulesTable)
            .options(joinedload(RulesTable.disease))
            .filter(RulesTable.id == rule_id)
            .first()
        )

    @staticmethod
    def create_rule(form) -> RulesTable:
        try:
            rule = RulesTable(
                disease_id=form.disease_id.data,
                certainty=form.certainty.data,
                explanation=form.explanation.data,
                is_active=form.is_active.data,
            )
            db.session.add(rule)
            db.session.commit()

            # Audit log
            log_audit(
                action="CREATE",
                table_name="Rules",
                record_id=rule.id,
                before_data=None,
                after_data={
                    "disease_id": rule.disease_id,
                    "certainty": rule.certainty,
                    "explanation": rule.explanation,
                    "is_active": rule.is_active,
                },
            )

            return rule

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_rule(rule: RulesTable, form) -> RulesTable:
        try:
            before_data = {
                "disease_id": rule.disease_id,
                "certainty": rule.certainty,
                "explanation": rule.explanation,
                "is_active": rule.is_active,
            }

            rule.disease_id = form.disease_id.data
            rule.certainty = form.certainty.data
            rule.explanation = form.explanation.data
            rule.is_active = form.is_active.data

            db.session.commit()

            log_audit(
                action="UPDATE",
                table_name="Rules",
                record_id=rule.id,
                before_data=before_data,
                after_data={
                    "disease_id": rule.disease_id,
                    "certainty": rule.certainty,
                    "explanation": rule.explanation,
                    "is_active": rule.is_active,
                },
            )

            return rule

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_rule(rule: RulesTable) -> None:
        try:
            before_data = {
                "disease_id": rule.disease_id,
                "certainty": rule.certainty,
                "explanation": rule.explanation,
                "is_active": rule.is_active,
            }

            db.session.delete(rule)
            db.session.commit()

            log_audit(
                action="DELETE",
                table_name="Rules",
                record_id=rule.id,
                before_data=before_data,
                after_data=None,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
