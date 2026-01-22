from typing import Optional, List
from extensions import db
from app.models.diseases import DiseaseTable
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from app.services.audit_service import log_audit  # ✅ Audit CSV
from flask import current_app


class DiseaseService:
    """Service layer for disease-related operations with audit logging"""

    # ---------- READ ---------- #
    @staticmethod
    def get_disease_all(page=1, per_page=10):
        """Get all diseases with pagination"""
        return db.paginate(
            db.select(DiseaseTable).order_by(DiseaseTable.id.desc()),
            page=page,
            per_page=per_page
        )

    @staticmethod
    def get_disease_by_id(disease_id: int) -> Optional[DiseaseTable]:
        """Get a disease by ID"""
        return db.session.get(DiseaseTable, disease_id)

    @staticmethod
    def search_diseases(disease_name=None, disease_type=None, severity_level=None, page=1, per_page=10):
        """Search and filter diseases"""
        query = db.select(DiseaseTable)

        if disease_name:
            query = query.where(DiseaseTable.disease_name.ilike(f"%{disease_name}%"))

        if disease_type:
            query = query.where(DiseaseTable.disease_type == disease_type)

        if severity_level:
            query = query.where(DiseaseTable.severity_level == severity_level)

        query = query.order_by(DiseaseTable.id.desc())
        return db.paginate(query, page=page, per_page=per_page)

    # ---------- CREATE ---------- #
    @staticmethod
    def create_disease(data: dict) -> DiseaseTable:
        """Create a new disease with audit logging"""
        if not data.get("disease_name"):
            raise ValueError("Disease name is required.")

        # Duplicate check
        duplicate = DiseaseTable.query.filter_by(disease_name=data.get("disease_name")).first()
        if duplicate:
            raise ValueError("This disease already exists.")

        disease = DiseaseTable(
            disease_name=data.get("disease_name"),
            disease_type=data.get("disease_type"),
            description=data.get("description"),
            severity_level=data.get("severity_level"),
            image=data.get("image"),
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(disease)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for CREATE
        log_audit(
            "CREATE",
            "diseases",
            disease.id,
            before_data=None,
            after_data={
                "disease_name": disease.disease_name,
                "disease_type": disease.disease_type,
                "description": disease.description,
                "severity_level": disease.severity_level,
                "image": disease.image,
                "is_active": disease.is_active
            }
        )

        return disease

    # ---------- UPDATE ---------- #
    @staticmethod
    def update_disease(disease_id: int, data: dict) -> Optional[DiseaseTable]:
        """Update an existing disease with audit logging"""
        disease = db.session.get(DiseaseTable, disease_id)
        if not disease:
            return None

        # Before snapshot
        before_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        # Update fields
        disease.disease_name = data.get("disease_name", disease.disease_name)
        disease.disease_type = data.get("disease_type", disease.disease_type)
        disease.description = data.get("description", disease.description)
        disease.severity_level = data.get("severity_level", disease.severity_level)
        disease.image = data.get("image", disease.image)
        disease.is_active = data.get("is_active", disease.is_active)

        # Duplicate name check
        duplicate = DiseaseTable.query.filter(
            DiseaseTable.id != disease.id,
            DiseaseTable.disease_name == disease.disease_name
        ).first()
        if duplicate:
            raise ValueError("Another disease with this name already exists.")

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # After snapshot
        after_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        # ✅ Audit log for UPDATE
        log_audit("UPDATE", "diseases", disease.id, before_data, after_data)

        return disease

    # ---------- DELETE ---------- #
    @staticmethod
    def delete_disease(disease_id: int) -> bool:
        """Delete a disease with audit logging"""
        disease = db.session.get(DiseaseTable, disease_id)
        if not disease:
            return False

        # Before snapshot
        before_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        try:
            db.session.delete(disease)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for DELETE
        log_audit("DELETE", "diseases", disease.id, before_data, after_data=None)
        return True

    # ---------- FILTERS ---------- #
    @staticmethod
    def get_active_diseases() -> List[DiseaseTable]:
        """Get all active diseases"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.is_active == True).all()

    @staticmethod
    def get_diseases_by_type(disease_type: str) -> List[DiseaseTable]:
        """Get all diseases of a specific type"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.disease_type == disease_type).all()

    @staticmethod
    def get_diseases_by_severity(severity_level: str) -> List[DiseaseTable]:
        """Get all diseases of a specific severity level"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.severity_level == severity_level).all()
