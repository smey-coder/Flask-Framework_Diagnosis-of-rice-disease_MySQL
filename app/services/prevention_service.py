import re
from typing import List, Optional

import cloudinary
from extensions import db
from app.models.preventions import PreventionTable
from app.models.diseases import DiseaseTable
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from werkzeug.utils import secure_filename
import os

from app.services.audit_service import log_audit

# ================= CONFIG ================= #

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_FOLDER = "static/images/preventions"

CLOUDINARY_FOLDER = "preventions"
# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file) -> str:
    # """Save image and return filename"""
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
    # """Delete old image from folder"""
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

    @staticmethod
    def get_by_disease(disease_id):

        try:

            return (
                PreventionTable.query
                .filter(
                    PreventionTable.disease_id == disease_id,
                    PreventionTable.is_active == True
                )
                .order_by(
                    PreventionTable.id.asc()
                )
                .all()
            )

        except Exception as e:

            print(
                f"Prevention Error: {e}"
            )

            return []

    # ---------- CREATE ---------- #

    @staticmethod
    def create(data: dict, image_file=None) -> PreventionTable:

        #Validation
        #Disease
        disease_id = data.get("disease_id")

        if not disease_id:
            raise ValueError("Disease is required")
        disease = DiseaseTable.query.get(disease_id)
        if not disease:
            raise ValueError("Disease disease does not exit.")

        #Prevention Type

        prevention_type = data.get("prevention_type")
        if not prevention_type:
            raise ValueError("Treatment type is required.")
        #Method
        method = (data.get("method") or "").strip()
        if not method:
            raise ValueError("Treatment method is required.")

        #image
        if not image_file or not allowed_file(image_file.filename):
            raise ValueError("Image is required and must be valid.")

        filename = save_image(image_file)

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

        # Check duplicates
        # duplicate = PreventionTable.query.filter_by(
        #     disease_id=data.get("disease_id"),
        #     prevention_type=data.get("prevention_type")
        # ).first()
        # if duplicate:
        #     delete_image(filename)
        #     raise ValueError(f"A prevention of type '{data.get('prevention_type')}' already exists for this disease.")


        #Create Object
        prevention = PreventionTable(
            disease_id=disease_id,
            prevention_type=prevention_type,
            method=method,
            description=data.get("description" or  "").strip(),
            priority=priority,
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

        # Audit log
        log_audit(
            "CREATE",
            "preventions",
            prevention.id,
            before_data=None,
            after_data={
                "disease_id": prevention.disease_id,
                "prevention_type": prevention.prevention_type,
                "method": prevention.method,
                "description": prevention.description,
                "priority": prevention.priority,
                "image": prevention.image,
                "is_active": prevention.is_active
            }
        )

        return prevention

    # ---------- UPDATE ---------- #

    @staticmethod
    def update(
        prevention: PreventionTable,
        data: dict,
        image_file=None
    ) -> PreventionTable:

        # =====================================================
        # BEFORE SNAPSHOT
        # =====================================================

        before_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "method": prevention.method,
            "description": prevention.description,
            "priority": prevention.priority,
            "image": prevention.image,
            "is_active": prevention.is_active
        }


        # =====================================================
        # VALIDATE DISEASE
        # =====================================================

        disease_id = data.get(
            "disease_id",
            prevention.disease_id
        )

        disease = DiseaseTable.query.get(disease_id)

        if not disease:
            raise ValueError(
                "Selected disease does not exist."
            )


        # =====================================================
        # IMAGE VARIABLES
        # =====================================================

        old_image = prevention.image
        new_image = None


        # =====================================================
        # HANDLE NEW IMAGE
        # =====================================================

        if image_file and image_file.filename:

            if not allowed_file(image_file.filename):
                raise ValueError(
                    "Invalid image format. "
                    "Only png, jpg, jpeg, gif, webp are allowed."
                )

            # Save NEW image first
            new_image = save_image(image_file)

            # Update model
            prevention.image = new_image


        # =====================================================
        # UPDATE DATA
        # =====================================================

        prevention.disease_id = disease_id

        prevention.prevention_type = data.get(
            "prevention_type",
            prevention.prevention_type
        )

        prevention.method = data.get(
            "method",
            prevention.method
        )

        prevention.description = data.get(
            "description",
            prevention.description
        )

        prevention.priority = data.get(
            "priority",
            prevention.priority
        )

        prevention.is_active = data.get(
            "is_active",
            prevention.is_active
        )


        # =====================================================
        # DATABASE COMMIT
        # =====================================================

        try:

            db.session.commit()

        except SQLAlchemyError as e:

            db.session.rollback()

            # Database failed
            # Delete NEW image because it is no longer used

            if new_image:
                delete_image(new_image)

            raise ValueError(
                f"Database error: {str(e)}"
            )


        # =====================================================
        # DELETE OLD IMAGE
        # Only after successful DB commit
        # =====================================================

        if (
            new_image
            and old_image
            and old_image != new_image
        ):
            delete_image(old_image)


        # =====================================================
        # AFTER SNAPSHOT
        # =====================================================

        after_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "method": prevention.method,
            "description": prevention.description,
            "priority": prevention.priority,
            "image": prevention.image,
            "is_active": prevention.is_active
        }


        # =====================================================
        # AUDIT LOG
        # =====================================================

        log_audit(
            "UPDATE",
            "preventions",
            prevention.id,
            before_data,
            after_data
        )


        return prevention

    # ---------- DELETE ---------- #

    @staticmethod
    def delete(prevention: PreventionTable):
        # Before snapshot
        before_data = {
            "disease_id": prevention.disease_id,
            "prevention_type": prevention.prevention_type,
            "method": prevention.method,
            "description": prevention.description,
            "priority": prevention.priority,
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

        # Audit log
        log_audit("DELETE", "preventions", prevention.id, before_data, after_data=None)
