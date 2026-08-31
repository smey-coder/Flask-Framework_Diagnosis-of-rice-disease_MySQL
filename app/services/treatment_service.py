import re
from typing import List, Optional
from venv import logger

import cloudinary
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

CLOUDINARY_FOLDER = "treatments"

# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file) -> str:
    # """Save image to static folder and return filename"""
    # filename = secure_filename(image_file.filename)
    # save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    # os.makedirs(save_path, exist_ok=True)
    # image_file.save(os.path.join(save_path, filename))
    # return filename
    """
    Upload image to Cloudinary (if configured/enabled), 
    otherwise fallback to saving in local static UPLOAD_FOLDER.
    """
    if not image_file or not allowed_file(image_file.filename):
        return None

    # 1. ព្យាយាម Upload ទៅ Cloudinary
    use_cloudinary = current_app.config.get("USE_CLOUDINARY", True)
    
    if use_cloudinary:
        try:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder=CLOUDINARY_FOLDER,
                resource_type="image"
            )
            # ត្រឡប់មកវិញនូវ Full HTTPS URL សម្រាប់រក្សាទុកក្នុង Database
            return upload_result.get("secure_url")
        except Exception as e:
            current_app.logger.warning(f"Cloudinary upload failed, falling back to local storage: {e}")
            image_file.seek(0)  # Reset pointer មុនពេល save ទៅ Local

    # 2. បើមិនប្រើ Cloudinary ឬ Cloudinary បរាជ័យ វានឹង save ចូល Local Storage
    try:
        filename = secure_filename(image_file.filename)
        save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(save_path, exist_ok=True)
        image_file.save(os.path.join(save_path, filename))
        return filename
    except Exception as e:
        current_app.logger.error(f"Local image save failed: {e}")
        return None


def delete_image(image_identifier: str):
    # """Delete old image from static folder"""
    # if not filename:
    #     return
    # file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    """
    Delete image automatically from Cloudinary (if URL) or Local static folder (if filename).
    """
    if not image_identifier:
        return

    # ករណី ១: រូបភាពនៅលើ Cloudinary (មាន http:// ឬ https://)
    if image_identifier.startswith("http://") or image_identifier.startswith("https://"):
        try:
            # ស្រង់យក Public ID ចេញពី Cloudinary URL (ឧទាហរណ៍: treatments/sample_id)
            match = re.search(rf"({CLOUDINARY_FOLDER}/[^./]+)", image_identifier)
            if match:
                public_id = match.group(1)
                cloudinary.uploader.destroy(public_id)
        except Exception as e:
            current_app.logger.error(f"Failed to delete Cloudinary image ({image_identifier}): {e}")

    # ករណី ២: រូបភាពនៅ Local Storage (ជា File Name ធម្មតា)
    else:
        try:
            file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, image_identifier)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.error(f"Failed to delete local image ({image_identifier}): {e}")


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

    @staticmethod
    def get_by_disease(disease_id):
        try:
            return (
                TreatmentTable.query
                .filter(
                    TreatmentTable.disease_id == disease_id,
                    TreatmentTable.is_active == True
                )
                .order_by(TreatmentTable.id.desc())
                .all()
            )

        except Exception as e:
            logger.error(
                f"Error getting treatments by disease: {e}"
            )
            return []

    #Treatment Recommended 
    @staticmethod
    def get_recommended_treatment(disease_id):
        try:

            treatment = (
                TreatmentTable.query
                .filter(
                    TreatmentTable.disease_id == disease_id,
                    TreatmentTable.is_active == True
                )
                .order_by(
                    TreatmentTable.priority.asc(),
                    TreatmentTable.id.asc()
                )
                .first()
            )

            return treatment

        except Exception as e:

            print(
                f"Treatment Recommendation Error: {e}"
            )
            return None

    @staticmethod
    def get_treatments_by_disease(disease_id):

        try:

            return (
                TreatmentTable.query
                .filter(
                    TreatmentTable.disease_id == disease_id,
                    TreatmentTable.is_active == True
                )
                .order_by(
                    TreatmentTable.priority.asc(),
                    TreatmentTable.id.asc()
                )
                .all()
            )

        except Exception as e:

            print(
                f"Treatment List Error: {e}"
            )

            return []
    # ---------- CREATE ---------- #
    @staticmethod
    def create(data: dict, image_file) -> TreatmentTable:

        # =====================================================
        # VALIDATION
        # =====================================================

        # -----------------------------------------------------
        # Disease
        # -----------------------------------------------------

        disease_id = data.get("disease_id")

        if not disease_id:
            raise ValueError("Disease is required.")

        disease = DiseaseTable.query.get(disease_id)

        if not disease:
            raise ValueError("Selected disease does not exist.")
        # -----------------------------------------------------
        # Treatment Type
        # -----------------------------------------------------

        treatment_type = data.get("treatment_type")

        if not treatment_type:
            raise ValueError("Treatment type is required.")
        # -----------------------------------------------------
        # Method
        # -----------------------------------------------------

        method = (data.get("method") or "").strip()

        if not method:
            raise ValueError("Treatment method is required.")

        # -----------------------------------------------------
        # Priority
        # -----------------------------------------------------

        priority = data.get("priority",1)

        try:
            priority = int(priority)
        except (TypeError,ValueError):
            raise ValueError("Priority must be a number.")

        if priority < 1 or priority > 10:
            raise ValueError("Priority must be between 1 and 10.")
        # -----------------------------------------------------
        # Image
        # -----------------------------------------------------

        if (not image_file or image_file.filename == ""):

            raise ValueError("Image is required.")

        if not allowed_file(image_file.filename):

            raise ValueError("Invalid image format.")

        # =====================================================
        # DUPLICATE CHECK
        # =====================================================

        # duplicate = (TreatmentTable.query.filter_by(disease_id=disease_id,treatment_type=treatment_type).first())

        # if duplicate:
        #     raise ValueError("This treatment type already exists ""for this disease.")

        # =====================================================
        # SAVE IMAGE
        # =====================================================

        filename = save_image(image_file)
        # =====================================================
        # CREATE OBJECT
        # =====================================================

        treatment = TreatmentTable(

            disease_id=disease_id,

            treatment_type=treatment_type,

            description=(data.get("description") or "").strip(),

            priority=priority,

            method=method,

            image=filename,

            is_active=data.get("is_active",True)
        )


        # =====================================================
        # DATABASE
        # =====================================================

        try:
            db.session.add(treatment)
            db.session.commit()
        except SQLAlchemyError as e:

            db.session.rollback()

            # Delete uploaded image
            # if database insert fails

            delete_image(filename)
            raise ValueError(f"Database error: {str(e)}")


        # =====================================================
        # AUDIT LOG
        # =====================================================

        log_audit(

            action="CREATE",

            table_name="treatments",

            record_id=treatment.id,

            before_data=None,

            after_data={

                "disease_id":
                    treatment.disease_id,

                "treatment_type":
                    treatment.treatment_type,

                "description":
                    treatment.description,

                "priority":
                    treatment.priority,

                "method":
                    treatment.method,

                "image":
                    treatment.image,

                "is_active":
                    treatment.is_active
            }
        )


        # =====================================================
        # RETURN
        # =====================================================

        return treatment


    # ---------- UPDATE ----------
    @staticmethod
    def update(
        treatment: TreatmentTable,
        data: dict,
        image_file=None
    ) -> TreatmentTable:

        # =====================================================
        # VALIDATION
        # =====================================================

        if not data.get("disease_id"):
            raise ValueError("Disease is required.")

        if not data.get("treatment_type"):
            raise ValueError("Treatment type is required.")

        disease = DiseaseTable.query.get(
            data.get("disease_id")
        )

        if not disease:
            raise ValueError(
                "Selected disease does not exist."
            )

        # =====================================================
        # PRIORITY VALIDATION
        # =====================================================

        priority = data.get("priority")

        if priority in (None, ""):
            priority = treatment.priority or 1

        try:
            priority = int(priority)
        except (TypeError, ValueError):
            raise ValueError(
                "Priority must be a number."
            )

        if priority < 1:
            raise ValueError(
                "Priority must be greater than or equal to 1."
            )

        # =====================================================
        # DUPLICATE VALIDATION
        # =====================================================

        # duplicate = TreatmentTable.query.filter(
        #     TreatmentTable.id != treatment.id,
        #     TreatmentTable.disease_id == data.get("disease_id"),
        #     TreatmentTable.treatment_type == data.get(
        #         "treatment_type"
        #     )
        # ).first()

        # if duplicate:
        #     raise ValueError(
        #         "This treatment type already exists for this disease."
        #     )

        # =====================================================
        # BEFORE SNAPSHOT
        # =====================================================

        before_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "method": treatment.method,
            "priority": treatment.priority,
            "image": treatment.image,
            "is_active": treatment.is_active
        }

        # =====================================================
        # IMAGE UPDATE
        # =====================================================

        old_image = treatment.image
        new_image = None

        if image_file and image_file.filename != "":

            if not allowed_file(image_file.filename):
                raise ValueError(
                    "Invalid image format."
                )

            new_image = save_image(image_file)

            treatment.image = new_image

        # =====================================================
        # UPDATE DATA
        # =====================================================

        treatment.disease_id = data.get(
            "disease_id"
        )

        treatment.treatment_type = data.get(
            "treatment_type"
        )

        treatment.description = data.get(
            "description",
            treatment.description
        )

        treatment.method = data.get(
            "method",
            treatment.method
        )

        treatment.priority = priority

        treatment.is_active = data.get(
            "is_active",
            treatment.is_active
        )

        # =====================================================
        # DATABASE COMMIT
        # =====================================================

        try:

            db.session.commit()

        except SQLAlchemyError as e:

            db.session.rollback()

            # Delete newly uploaded image
            if new_image:
                delete_image(new_image)

            raise ValueError(
                f"Database error: {str(e)}"
            )

        # =====================================================
        # DELETE OLD IMAGE
        # =====================================================

        if new_image and old_image:
            delete_image(old_image)

        # =====================================================
        # AFTER SNAPSHOT
        # =====================================================

        after_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "method": treatment.method,
            "priority": treatment.priority,
            "image": treatment.image,
            "is_active": treatment.is_active
        }

        # =====================================================
        # AUDIT LOG
        # =====================================================

        log_audit(
            action="UPDATE",
            table_name="treatments",
            record_id=treatment.id,
            before_data=before_data,
            after_data=after_data
        )

        return treatment
    # ---------- DELETE ---------- #
    @staticmethod
    def delete(treatment: TreatmentTable):
        # --- BEFORE SNAPSHOT ---
        before_data = {
            "disease_id": treatment.disease_id,
            "treatment_type": treatment.treatment_type,
            "description": treatment.description,
            "priority": treatment.priority,
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
