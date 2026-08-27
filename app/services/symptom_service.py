import os
import uuid
from typing import Optional, List, Union
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.models.symptoms import SymptomsTable
from app.services.audit_service import log_audit

# ================= CONFIG ================= #
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_FOLDER = "static/images/symptoms"


# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file) -> str:
    """Save image to UPLOAD_FOLDER with unique UUID prefix and return filename."""
    original_filename = secure_filename(image_file.filename)
    extension = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "jpg"
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

    save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(save_path, exist_ok=True)
    image_file.save(os.path.join(save_path, unique_filename))
    return unique_filename


def delete_image(filename: str):
    """Delete image from UPLOAD_FOLDER."""
    if not filename:
        return
    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            current_app.logger.warning(f"Failed to delete image file {file_path}: {e}")


# ================= SERVICE ================= #

class SymptomService:
    """Service layer for symptom-related operations matching DiseaseService architecture"""

    # ---------- READ ---------- #

    @staticmethod
    def get_symptom_all(page=1, per_page=10):
        """Get all symptoms with pagination"""
        return SymptomsTable.query.order_by(SymptomsTable.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_symptom_by_id(symptom_id: int) -> Optional[SymptomsTable]:
        """Retrieve a symptom by ID"""
        return SymptomsTable.query.get(symptom_id)

    @staticmethod
    def search_symptoms(symptom_name=None, symptom_group=None, is_active=None, page=1, per_page=10):
        """Search symptoms by filters with pagination"""
        query = SymptomsTable.query

        if symptom_name:
            query = query.filter(SymptomsTable.symptom_name.ilike(f"%{symptom_name}%"))
        if symptom_group:
            query = query.filter(SymptomsTable.symptom_group == symptom_group)

        # Status filter
        if is_active is not None and is_active != "":
            if is_active in ("1", True, 1, "true", "True"):
                query = query.filter(SymptomsTable.is_active.is_(True))
            elif is_active in ("0", False, 0, "false", "False"):
                query = query.filter(SymptomsTable.is_active.is_(False))

        query = query.order_by(SymptomsTable.id.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    # ---------- CREATE ---------- #

    @staticmethod
    def create_symptom(
        data: Optional[dict] = None,
        symptom_name: Optional[str] = None,
        symptom_group: Optional[str] = None,
        description: Optional[str] = "",
        is_active: bool = True,
        image_file=None,
    ) -> SymptomsTable:
        """Create a new symptom with flexible parameter input (dict or kwargs)."""
        if data and isinstance(data, dict):
            symptom_name = data.get("symptom_name", symptom_name)
            symptom_group = data.get("symptom_group", symptom_group)
            description = data.get("description", description)
            is_active = data.get("is_active", is_active)

        if not symptom_name or not symptom_name.strip():
            raise ValueError("Symptom name is required.")

        symptom_name = symptom_name.strip()
        filename = ""

        try:
            # 1. Check duplicate name
            duplicate = SymptomsTable.query.filter_by(symptom_name=symptom_name).first()
            if duplicate:
                raise ValueError("This symptom already exists.")

            # 2. Upload image if provided
            if image_file and hasattr(image_file, "filename") and image_file.filename:
                if not allowed_file(image_file.filename):
                    raise ValueError(f"Invalid image format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
                filename = save_image(image_file)

            # 3. Instantiate model
            symptom = SymptomsTable(
                symptom_name=symptom_name,
                symptom_group=symptom_group,
                description=description or "",
                image=filename,
                is_active=is_active if is_active is not None else True,
            )

            db.session.add(symptom)
            db.session.commit()

            # 4. Audit log
            log_audit(
                "CREATE",
                "symptoms",
                symptom.id,
                before_data=None,
                after_data={
                    "symptom_name": symptom.symptom_name,
                    "symptom_group": symptom.symptom_group,
                    "description": symptom.description,
                    "image": symptom.image,
                    "is_active": symptom.is_active,
                },
            )

            return symptom

        except SQLAlchemyError as e:
            db.session.rollback()
            if filename:
                delete_image(filename)
            raise ValueError(f"Database error: {str(e)}")

        except Exception as e:
            db.session.rollback()
            if filename:
                delete_image(filename)
            raise e

    # ---------- UPDATE ---------- #

    @staticmethod
    def update_symptom(
        symptom_id: int, data: dict, image_file=None
    ) -> Optional[SymptomsTable]:
        """Update an existing symptom with optional image upload and audit logging"""
        symptom = SymptomsTable.query.get(symptom_id)
        if not symptom:
            raise ValueError("Symptom not found.")

        # Snapshot before update
        before_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "image": symptom.image,
            "is_active": symptom.is_active,
        }

        old_image = symptom.image
        new_filename = None

        # Process new image upload if present
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            if not allowed_file(image_file.filename):
                raise ValueError(f"Invalid image format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
            new_filename = save_image(image_file)
            symptom.image = new_filename

        # Update text fields
        new_name = data.get("symptom_name", symptom.symptom_name)
        if new_name:
            new_name = new_name.strip()

        # Duplicate check if name changed
        duplicate = SymptomsTable.query.filter(
            SymptomsTable.id != symptom.id,
            SymptomsTable.symptom_name == new_name,
        ).first()

        if duplicate:
            if new_filename:
                delete_image(new_filename)
            raise ValueError("Another symptom with this name already exists.")

        symptom.symptom_name = new_name
        symptom.symptom_group = data.get("symptom_group", symptom.symptom_group)
        symptom.description = data.get("description", symptom.description)
        symptom.is_active = data.get("is_active", symptom.is_active)

        try:
            db.session.commit()

            # Delete old image only after successful DB commit
            if new_filename and old_image:
                delete_image(old_image)

        except SQLAlchemyError as e:
            db.session.rollback()
            if new_filename:
                delete_image(new_filename)
            raise ValueError(f"Database error: {str(e)}")

        # Snapshot after update
        after_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "image": symptom.image,
            "is_active": symptom.is_active,
        }

        # Audit log
        log_audit("UPDATE", "symptoms", symptom.id, before_data, after_data)

        return symptom

    # ---------- DELETE ---------- #

    @staticmethod
    def delete_symptom(symptom_id: int) -> bool:
        """Delete a symptom with relational constraint handling and file cleanup"""
        symptom = SymptomsTable.query.get(symptom_id)
        if not symptom:
            raise ValueError("Symptom not found.")

        before_data = {
            "symptom_name": symptom.symptom_name,
            "symptom_group": symptom.symptom_group,
            "description": symptom.description,
            "image": symptom.image,
            "is_active": symptom.is_active,
        }

        image_filename = symptom.image

        try:
            db.session.delete(symptom)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()

            if "foreign key constraint" in str(e).lower():
                raise ValueError(
                    "Cannot delete this symptom because it is linked to rules or diseases."
                )

            raise ValueError(f"Database error: {str(e)}")

        # Delete image from static storage after DB removal succeeds
        if image_filename:
            delete_image(image_filename)

        # Audit log
        log_audit("DELETE", "symptoms", symptom_id, before_data, after_data=None)

        return True

    # ---------- FILTERS ---------- #

    @staticmethod
    def get_active_symptoms() -> List[SymptomsTable]:
        """Get list of active symptoms for dropdowns or expert rules"""
        return SymptomsTable.query.filter_by(is_active=True).all()

    @staticmethod
    def get_symptoms_by_group(symptom_group: str) -> List[SymptomsTable]:
        """Filter symptoms by group (e.g., Leaf, Stem, Grain)"""
        return SymptomsTable.query.filter_by(symptom_group=symptom_group).all()