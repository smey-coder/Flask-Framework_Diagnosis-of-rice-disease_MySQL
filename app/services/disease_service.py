from typing import Optional, List

import cloudinary
from app.models.UserNotification import UserNotification
from app.models.user import UserTable
from extensions import db
from app.models.diseases import DiseaseTable
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from werkzeug.utils import secure_filename
import os
import cloudinary.uploader
import cloudinary.api

from app.services.audit_service import log_audit

# ================= CONFIG ================= #
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = "static/images/diseases"

CLOUDINARY_FOLDER = "diseases"

# ================= HELPERS ================= #

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image_file) -> str:
    """Save image to UPLOAD_FOLDER and return filename."""
    # filename = secure_filename(image_file.filename)
    # save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    # os.makedirs(save_path, exist_ok=True)
    # image_file.save(os.path.join(save_path, filename))
    # return filename
    
    #Cloude cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder=CLOUDINARY_FOLDER,
            resource_type="image"
        )
        # Return the complete https URL to save in your database
        return upload_result.get("secure_url")
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload failed: {e}")
        return None

def delete_image(image_url_or_id: str):
    """Delete image from UPLOAD_FOLDER."""
    # if not filename:
    #     return
    # file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    # if os.path.exists(file_path):
    #     os.remove(file_path)

    #Store in Cloudinary
    """Delete image from Cloudinary using its public ID or full URL."""
    if not image_url_or_id:
        return
        
    try:
        # If full URL is passed, extract public_id (e.g., 'diseases/sample_id')
        if "cloudinary.com" in image_url_or_id:
            # Extract 'diseases/filename' without extension
            parts = image_url_or_id.split("/")
            filename_with_ext = parts[-1]
            public_id_name = filename_with_ext.rsplit(".", 1)[0]
            public_id = f"{CLOUDINARY_FOLDER}/{public_id_name}"
        else:
            public_id = image_url_or_id

        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        current_app.logger.error(f"Cloudinary deletion failed: {e}")

# ================= SERVICE ================= #

class DiseaseService:

    # ---------- READ ---------- #

    @staticmethod
    def get_disease_all(page=1, per_page=10):
        """Get all diseases with pagination"""
        return DiseaseTable.query.order_by(DiseaseTable.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_disease_by_id(disease_id: int) -> Optional[DiseaseTable]:
        return DiseaseTable.query.get(disease_id)

    @staticmethod
    def search_diseases(disease_name=None, disease_type=None, severity_level=None, is_active=None,page=1, per_page=10):
        """Search diseases by filters with pagination"""
        query = DiseaseTable.query
        if disease_name:
            query = query.filter(DiseaseTable.disease_name.ilike(f"%{disease_name}%"))
        if disease_type:
            query = query.filter(DiseaseTable.disease_type == disease_type)
        if severity_level:
            query = query.filter(DiseaseTable.severity_level == severity_level)

        # Status
        if is_active is not None:

            if is_active == "1":
                query = query.filter(
                    DiseaseTable.is_active.is_(True)
                )

            elif is_active == "0":
                query = query.filter(
                    DiseaseTable.is_active.is_(False)
                )
        query = query.order_by(DiseaseTable.id.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    # ---------- CREATE ---------- #
    @staticmethod
    def create_disease(data: dict, image_file=None) -> DiseaseTable:
        """Create a new disease with optional image upload"""

        filename = ""

        try:
            # ==========================================
            # 1. Upload image
            # ==========================================
            if image_file:

                if not allowed_file(image_file.filename):
                    raise ValueError(
                        "Invalid image format. Allowed: png, jpg, jpeg, gif"
                    )

                filename = save_image(image_file)

            # ==========================================
            # 2. Create disease
            # ==========================================
            disease = DiseaseTable(
                disease_name=data["disease_name"],
                disease_type=data["disease_type"],
                description=data.get("description", ""),
                severity_level=data.get("severity_level", "Low"),
                image=filename,
                is_active=data.get("is_active", True)
            )

            db.session.add(disease)

            # IMPORTANT:
            # Generate disease.id before creating notification
            db.session.flush()

            print("Disease created:", disease.id)

            # ==========================================
            # 3. Get all users
            # ==========================================
            users = UserTable.query.all()

            print("Total users:", len(users))

            # ==========================================
            # 4. Create notification for ALL users
            # ==========================================
            for user in users:

                notification = UserNotification(
                    user_id=user.id,
                    disease_id=disease.id,
                    monitoring_id=None,
                    category="disease",
                    is_read=False,
                    is_deleted=False
                )

                # IMPORTANT:
                # Add notification INSIDE the loop
                db.session.add(notification)

                print(
                    f"Notification created "
                    f"for user {user.id}, "
                    f"disease {disease.id}"
                )

            # ==========================================
            # 5. Commit disease + notifications
            # ==========================================
            db.session.commit()

            # ==========================================
            # 6. Audit log
            # ==========================================
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

        except SQLAlchemyError as e:

            db.session.rollback()

            if filename:
                delete_image(filename)

            raise ValueError(
                f"Database error: {str(e)}"
            )

        except Exception as e:

            db.session.rollback()

            if filename:
                delete_image(filename)

            raise



    # ---------- UPDATE ---------- #

    @staticmethod
    def update_disease(disease_id: int, data: dict, image_file=None) -> Optional[DiseaseTable]:
        disease = DiseaseTable.query.get(disease_id)
        if not disease:
            return None

        # Snapshot before
        before_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        # Handle image upload
        old_image = disease.image  # store old image name for potential delete
        if image_file and hasattr(image_file, 'filename') and image_file.filename:
            if image_file:
                if not allowed_file(image_file.filename):
                    raise ValueError("Invalid image format. Allowed: png, jpg, jpeg, gif")
                new_filename = save_image(image_file)
                disease.image = new_filename
                if old_image:
                    delete_image(old_image)

        # Update fields
        disease.disease_name = data.get("disease_name", disease.disease_name)
        disease.disease_type = data.get("disease_type", disease.disease_type)
        disease.description = data.get("description", disease.description)
        disease.severity_level = data.get("severity_level", disease.severity_level)
        disease.is_active = data.get("is_active", disease.is_active)

        # Check duplicate name
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
            if image_file:
                delete_image(disease.image)
                disease.image = old_image
            raise ValueError(f"Database error: {str(e)}")

        # Snapshot after
        after_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        # ✅ Audit log
        log_audit("UPDATE", "diseases", disease.id, before_data, after_data)

        return disease

    # ---------- DELETE ---------- #

    @staticmethod
    def delete_disease(disease_id: int) -> bool:
        disease = DiseaseTable.query.get(disease_id)
        if not disease:
            raise ValueError("Disease not found.")
        # Snapshot before delete (for audit)
        before_data = {
            "disease_name": disease.disease_name,
            "disease_type": disease.disease_type,
            "description": disease.description,
            "severity_level": disease.severity_level,
            "image": disease.image,
            "is_active": disease.is_active
        }

        image_filename = disease.image  # store before delete

        try:
            # ✅ Delete from DB
            db.session.delete(disease)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()

            # ✅ Handle foreign key error (IMPORTANT)
            if "foreign key constraint" in str(e).lower():
                raise ValueError(
                    "Cannot delete this disease because it is linked to other records (symptoms, treatments, etc)."
                )

            raise ValueError(f"Database error: {str(e)}")

        # ✅ Delete image AFTER DB success
        if image_filename:
            try:
                delete_image(image_filename)
            except Exception as img_err:
                # don't break system if image delete fails
                print(f"Image delete warning: {img_err}")

        # ✅ Audit log
        log_audit("DELETE", "diseases", disease_id, before_data, after_data=None)

        return True
    # ---------- FILTERS ---------- #
    @staticmethod
    def get_active_diseases() -> List[DiseaseTable]:
        return DiseaseTable.query.filter_by(is_active=True).all()

    @staticmethod
    def get_diseases_by_type(disease_type: str) -> List[DiseaseTable]:
        return DiseaseTable.query.filter_by(disease_type=disease_type).all()

    @staticmethod
    def get_diseases_by_severity(severity_level: str) -> List[DiseaseTable]:
        return DiseaseTable.query.filter_by(severity_level=severity_level).all()