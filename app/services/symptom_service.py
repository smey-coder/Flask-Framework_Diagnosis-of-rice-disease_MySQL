from typing import Optional, List
from extensions import db
from app.models.symptoms import SymptomsTable
from sqlalchemy.exc import SQLAlchemyError
from app.services.audit_service import log_audit  # ✅ Audit CSV


class SymptomService:
    """Service layer for symptom-related operations with audit logging"""

    # ---------- READ ---------- #
    @staticmethod
    def get_symptom_all() -> List[SymptomsTable]:
        """Retrieve all symptoms"""
        return SymptomsTable.query.order_by(SymptomsTable.id.desc()).all()

    @staticmethod
    def get_symptom_by_id(symptom_id: int) -> Optional[SymptomsTable]:
        """Retrieve a symptom by ID"""
        return db.session.get(SymptomsTable, symptom_id)

    # ---------- CREATE ---------- #
    @staticmethod
    def create_symptom(data: dict) -> SymptomsTable:
        """Create a new symptom with audit logging"""
        if not data.get("symptom_name"):
            raise ValueError("Symptom name is required.")

        # Duplicate check
        duplicate = SymptomsTable.query.filter_by(symptom_name=data.get("symptom_name")).first()
        if duplicate:
            raise ValueError("This symptom already exists.")

        symptom = SymptomsTable(
            symptom_name=data.get("symptom_name"),
            symptom_group=data.get("symptom_group"),
            description=data.get("description"),
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(symptom)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for CREATE
        log_audit(
            "CREATE",
            "symptoms",
            symptom.id,
            before_data=None,
            after_data={
                "symptom_name": symptom.symptom_name,
                "symptom_group": symptom.symptom_group,
                "description": symptom.description,
                "is_active": symptom.is_active
            }
        )

        return symptom

    # ---------- UPDATE ---------- #
    @staticmethod
    def update_symptom(symptom: SymptomsTable, data: dict) -> SymptomsTable:
        """Update an existing symptom with audit logging"""

        # Before snapshot
        before_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "is_active": symptom.is_active
        }

        # Update fields
        symptom.symptom_name = data.get("symptom_name", symptom.symptom_name)
        symptom.symptom_group = data.get("symptom_group", symptom.symptom_group)
        symptom.description = data.get("description", symptom.description)
        symptom.is_active = data.get("is_active", symptom.is_active)

        # Duplicate check
        duplicate = SymptomsTable.query.filter(
            SymptomsTable.id != symptom.id,
            SymptomsTable.symptom_name == symptom.symptom_name
        ).first()
        if duplicate:
            raise ValueError("Another symptom with this name already exists.")

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # After snapshot
        after_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "is_active": symptom.is_active
        }

        # ✅ Audit log for UPDATE
        log_audit("UPDATE", "symptoms", symptom.id, before_data, after_data)

        return symptom

    # ---------- DELETE ---------- #
    @staticmethod
    def delete_symptom(symptom: SymptomsTable) -> None:
        """Delete a symptom with audit logging"""

        # Before snapshot
        before_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "is_active": symptom.is_active
        }

        try:
            db.session.delete(symptom)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for DELETE
        log_audit("DELETE", "symptoms", symptom.id, before_data, after_data=None)
