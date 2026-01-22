from typing import List, Optional
from extensions import db
from app.models.preventions import PreventionTable
from app.models.diseases import DiseaseTable
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from werkzeug.utils import secure_filename
import os

from app.services.audit_service import log_audit

# ================= CONFIG ================= #

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = "static/images/preventions"


# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file) -> str:
    """Save image and return filename"""
    filename = secure_filename(image_file.filename)
    save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(save_path, exist_ok=True)
    image_file.save(os.path.join(save_path, filename))
    return filename


def delete_image(filename: str):
    """Delete old image from folder"""
    if not filename:
        return
    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


# ================= SERVICE ================= #

class PreventionService:

    # ---------- READ ---------- #

    @staticmethod
    def get_all(active_only: bool = False) -> List[PreventionTable]:
        query = PreventionTable.query.order_by(PreventionTable.id.desc())
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_by_id(prevention_id: int) -> Optional[PreventionTable]:
        return PreventionTable.query.get_or_404(prevention_id)

    # ---------- CREATE ---------- #

    @staticmethod
    def create(data: dict, image_file=None) -> PreventionTable:
        if not image_file or not allowed_file(image_file.filename):
            raise ValueError("Image is required and must be valid.")

        filename = save_image(image_file)

        # Check duplicates
        duplicate = PreventionTable.query.filter_by(
            disease_id=data.get("disease_id"),
            prevention_type=data.get("prevention_type")
        ).first()
        if duplicate:
            delete_image(filename)
            raise ValueError(f"A prevention of type '{data.get('prevention_type')}' already exists for this disease.")

        prevention = PreventionTable(
            disease_id=data.get("disease_id"),
            prevention_type=data.get("prevention_type"),
            description=data.get("description", ""),
            image=filename,
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(prevention)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            delete_image(filename)
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log
        log_audit(
            "CREATE",
            "preventions",
            prevention.id,
            before_data=None,
            after_data={
                "disease_id": prevention.disease_id,
                "prevention_type": prevention.prevention_type,
                "description": prevention.description,
                "image": prevention.image,
                "is_active": prevention.is_active
            }
        )

        return prevention

    # ---------- UPDATE ---------- #

    @staticmethod
    def update(prevention: PreventionTable, data: dict, image_file=None) -> PreventionTable:
        # Before snapshot
        before_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "description": prevention.description,
            "image": prevention.image,
            "is_active": prevention.is_active
        }

        # Check duplicates
        duplicate = PreventionTable.query.filter(
            PreventionTable.id != prevention.id,
            PreventionTable.disease_id == data.get("disease_id"),
            PreventionTable.prevention_type == data.get("prevention_type")
        ).first()
        if duplicate:
            raise ValueError(f"A prevention of type '{data.get('prevention_type')}' already exists for this disease.")

        # Handle image update
        if image_file and allowed_file(image_file.filename):
            old_image = prevention.image
            filename = save_image(image_file)
            prevention.image = filename
            delete_image(old_image)

        prevention.disease_id = data.get("disease_id", prevention.disease_id)
        prevention.prevention_type = data.get("prevention_type", prevention.prevention_type)
        prevention.description = data.get("description", prevention.description)
        prevention.is_active = data.get("is_active", prevention.is_active)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # After snapshot
        after_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "description": prevention.description,
            "image": prevention.image,
            "is_active": prevention.is_active
        }

        # ✅ Audit log
        log_audit("UPDATE", "preventions", prevention.id, before_data, after_data)

        return prevention

    # ---------- DELETE ---------- #

    @staticmethod
    def delete(prevention: PreventionTable):
        # Before snapshot
        before_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "description": prevention.description,
            "image": prevention.image,
            "is_active": prevention.is_active
        }

        image = prevention.image

        try:
            db.session.delete(prevention)
            db.session.commit()
            delete_image(image)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log
        log_audit("DELETE", "preventions", prevention.id, before_data, after_data=None)
