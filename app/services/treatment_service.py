from typing import List, Optional
from extensions import db
from app.models.treatments import TreatmentTable
from app.models.diseases import DiseaseTable
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from werkzeug.utils import secure_filename
import os

from app.services.audit_service import log_audit

# ================= CONFIG ================= #
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = "static/images/treatments"

# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file) -> str:
    """Save image to static folder and return filename"""
    filename = secure_filename(image_file.filename)
    save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(save_path, exist_ok=True)
    image_file.save(os.path.join(save_path, filename))
    return filename


def delete_image(filename: str):
    """Delete old image from static folder"""
    if not filename:
        return
    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


# ================= SERVICE ================= #
class TreatmentService:

    # ---------- READ ---------- #
    @staticmethod
    def get_all(active_only: bool = False) -> List[TreatmentTable]:
        query = TreatmentTable.query.order_by(TreatmentTable.id.desc())
        if active_only:
            query = query.filter(TreatmentTable.is_active.is_(True))
        return query.all()

    @staticmethod
    def get_by_id(treatment_id: int) -> Optional[TreatmentTable]:
        return TreatmentTable.query.get(treatment_id)

    # ---------- CREATE ---------- #
    @staticmethod
    def create(data: dict, image_file) -> TreatmentTable:
        # --- VALIDATION ---
        if not data.get("disease_id"):
            raise ValueError("Disease is required.")
        if not data.get("treatment_type"):
            raise ValueError("Treatment type is required.")

        disease = DiseaseTable.query.get(data.get("disease_id"))
        if not disease:
            raise ValueError("Selected disease does not exist.")

        if not image_file or image_file.filename == "":
            raise ValueError("Image is required.")
        if not allowed_file(image_file.filename):
            raise ValueError("Invalid image format.")

        duplicate = TreatmentTable.query.filter_by(
            disease_id=data.get("disease_id"),
            treatment_type=data.get("treatment_type")
        ).first()
        if duplicate:
            raise ValueError("This treatment type already exists for this disease.")

        # --- SAVE IMAGE ---
        filename = save_image(image_file)

        # --- CREATE OBJECT ---
        treatment = TreatmentTable(
            disease_id=data.get("disease_id"),
            treatment_type=data.get("treatment_type"),
            description=data.get("description", ""),
            method=data.get("method", ""),
            image=filename,
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(treatment)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            delete_image(filename)
            raise ValueError(f"Database error: {str(e)}")

        # --- AUDIT LOG ---
        log_audit(
            action="CREATE",
            table_name="treatments",
            record_id=treatment.id,
            before_data=None,
            after_data={
                "disease_id": treatment.disease_id,
                "treatment_type": treatment.treatment_type,
                "description": treatment.description,
                "method": treatment.method,
                "is_active": treatment.is_active
            }
        )

        return treatment

    # ---------- UPDATE ---------- #
    @staticmethod
    def update(treatment: TreatmentTable, data: dict, image_file=None) -> TreatmentTable:
        if not data.get("disease_id"):
            raise ValueError("Disease is required.")
        disease = DiseaseTable.query.get(data.get("disease_id"))
        if not disease:
            raise ValueError("Selected disease does not exist.")

        duplicate = TreatmentTable.query.filter(
            TreatmentTable.id != treatment.id,
            TreatmentTable.disease_id == data.get("disease_id"),
            TreatmentTable.treatment_type == data.get("treatment_type")
        ).first()
        if duplicate:
            raise ValueError("This treatment type already exists for this disease.")

        # --- BEFORE SNAPSHOT ---
        before_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "method": treatment.method,
            "image": treatment.image,
            "is_active": treatment.is_active
        }

        # --- IMAGE UPDATE ---
        if image_file and image_file.filename != "":
            if not allowed_file(image_file.filename):
                raise ValueError("Invalid image format.")
            old_image = treatment.image
            filename = save_image(image_file)
            treatment.image = filename
            delete_image(old_image)

        # --- UPDATE DATA ---
        treatment.disease_id = data.get("disease_id")
        treatment.treatment_type = data.get("treatment_type")
        treatment.description = data.get("description", treatment.description)
        treatment.method = data.get("method", treatment.method)
        treatment.is_active = data.get("is_active", treatment.is_active)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # --- AFTER SNAPSHOT ---
        after_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "method": treatment.method,
            "image": treatment.image,
            "is_active": treatment.is_active
        }

        # --- AUDIT LOG ---
        log_audit("UPDATE", "treatments", treatment.id, before_data, after_data)

        return treatment

    # ---------- DELETE ---------- #
    @staticmethod
    def delete(treatment: TreatmentTable):
        # --- BEFORE SNAPSHOT ---
        before_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "method": treatment.method,
            "image": treatment.image,
            "is_active": treatment.is_active
        }

        image = treatment.image

        try:
            db.session.delete(treatment)
            db.session.commit()
            delete_image(image)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # --- AUDIT LOG ---
        log_audit("DELETE", "treatments", treatment.id, before_data, None)
