import os
import uuid
import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

from extensions import db
from app.models import UserTable


class ProfileService:

    # =========================================================
    # Allowed Profile Image Extensions
    # =========================================================
    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp",
    }

    # Maximum image size: 2 MB
    MAX_FILE_SIZE = 2 * 1024 * 1024

    # =========================================================
    # Get Profile
    # =========================================================
    @staticmethod
    def get_profile(user_id):

        try:
            return UserTable.query.get(user_id)

        except Exception as e:

            current_app.logger.exception(
                f"Get Profile Error: {e}"
            )

            return None

    # =========================================================
    # Update Profile Information
    # =========================================================
    @staticmethod
    def update_profile(user_id, data):

        try:

            user = UserTable.query.get(user_id)

            if not user:
                return None

            # -----------------------------------------
            # Update Full Name
            # -----------------------------------------

            if "full_name" in data:
                full_name = data.get("full_name")

                if full_name:
                    user.full_name = full_name.strip()

            # -----------------------------------------
            # Update Email
            # -----------------------------------------

            if "email" in data:

                email = data.get("email")

                if email:
                    user.email = email.strip().lower()

            db.session.commit()

            return user

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                f"Update Profile Error: {e}"
            )

            return None

    # =========================================================
    # Check Allowed Image
    # =========================================================
    @staticmethod
    def allowed_file(filename):

        if not filename:
            return False

        if "." not in filename:
            return False

        extension = filename.rsplit(".",1)[1].lower()

        return extension in ProfileService.ALLOWED_EXTENSIONS

    # =========================================================
    # Get Upload Folder local 
    # =========================================================
    @staticmethod
    def get_upload_folder():

        upload_folder = os.path.join(
            current_app.static_folder,
            "uploads",
            "profiles"
        )

        # Create folder if it doesn't exist
        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        return upload_folder

    # =========================================================
    # Generate Unique Filename
    # =========================================================
    @staticmethod
    def generate_filename(user_id, original_filename):

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        unique_id = uuid.uuid4().hex[:12]

        filename = (
            f"user_{user_id}_{unique_id}.{extension}"
        )

        return secure_filename(filename)

    # =========================================================
    # Delete Old Profile Image
    # =========================================================
    @staticmethod
    def delete_old_image(user):

        # if not user:
        #     return

        # if not user.image:
        #     return

        # old_path = os.path.join(
        #     current_app.static_folder,
        #     user.image
        # )

        # # Check whether file exists
        # if os.path.exists(old_path):

        #     try:

        #         os.remove(old_path)

        #     except OSError as e:

        #         current_app.logger.warning(
        #             f"Unable to delete old profile image: {e}"
        #         )
        #Store in Cloudinary 
        if not user or not user.image:
            return

        try:
            # Check if user model stores public_id separately,
            # otherwise extract public_id from the Cloudinary URL
            if hasattr(user, "image_public_id") and user.image_public_id:
                cloudinary.uploader.destroy(user.image_public_id)
            elif "cloudinary.com" in user.image:
                # Extracts 'folder/filename' without extension from standard Cloudinary URL
                public_id = (
                    user.image.split("/")[-2] + "/" + user.image.split("/")[-1].rsplit(".", 1)[0]
                    if "profiles/" in user.image
                    else user.image.split("/")[-1].rsplit(".", 1)[0]
                )
                cloudinary.uploader.destroy(public_id)
        except Exception as e:
            current_app.logger.warning(f"Unable to delete old profile image from Cloudinary: {e}")

    # =========================================================
    # Upload / Change Profile Image
    # =========================================================
    @staticmethod
    def upload_profile_image(user_id, file):

        # try:

        #     # -----------------------------------------
        #     # Validate file
        #     # -----------------------------------------

        #     if not file:

        #         return (
        #             False,
        #             "Please select an image."
        #         )

        #     if not file.filename:

        #         return (
        #             False,
        #             "Please select an image."
        #         )

        #     # -----------------------------------------
        #     # Validate extension
        #     # -----------------------------------------

        #     if not ProfileService.allowed_file(
        #         file.filename
        #     ):

        #         return (
        #             False,
        #             "Invalid image format. "
        #             "Allowed: JPG, JPEG, PNG and WEBP."
        #         )

        #     # -----------------------------------------
        #     # Check file size
        #     # -----------------------------------------

        #     file.seek(0, os.SEEK_END)

        #     file_size = file.tell()

        #     file.seek(0)

        #     if file_size > ProfileService.MAX_FILE_SIZE:

        #         return (
        #             False,
        #             "Image size must be less than 2 MB."
        #         )

        #     # -----------------------------------------
        #     # Find User
        #     # -----------------------------------------

        #     user = UserTable.query.get(user_id)

        #     if not user:

        #         return (
        #             False,
        #             "User not found."
        #         )

        #     # -----------------------------------------
        #     # Get Upload Folder
        #     # -----------------------------------------

        #     upload_folder = (
        #         ProfileService.get_upload_folder()
        #     )

        #     # -----------------------------------------
        #     # Generate New Filename
        #     # -----------------------------------------

        #     filename = (
        #         ProfileService.generate_filename(
        #             user.id,
        #             file.filename
        #         )
        #     )

        #     file_path = os.path.join(
        #         upload_folder,
        #         filename
        #     )

        #     # -----------------------------------------
        #     # Delete Previous Image
        #     # -----------------------------------------

        #     ProfileService.delete_old_image(user)

        #     # -----------------------------------------
        #     # Save New Image
        #     # -----------------------------------------

        #     file.save(file_path)

        #     # -----------------------------------------
        #     # Save Relative Path to Database
        #     # -----------------------------------------

        #     user.image = os.path.join(
        #         "uploads",
        #         "profiles",
        #         filename
        #     ).replace("\\", "/")

        #     db.session.commit()

        #     return (
        #         True,
        #         "Profile image updated successfully."
        #     )

        # except Exception as e:

        #     db.session.rollback()

        #     current_app.logger.exception(
        #         f"Upload Profile Image Error: {e}"
        #     )

        #     return (
        #         False,
        #         "Unable to upload profile image."
        #     )
        #Store in Cloudinary 
        try:
            if not file or not file.filename:
                return False, "Please select an image."

            if not ProfileService.allowed_file(file.filename):
                return (
                    False,
                    "Invalid image format. Allowed: JPG, JPEG, PNG and WEBP.",
                )

            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > ProfileService.MAX_FILE_SIZE:
                return False, "Image size must be less than 2 MB."

            user = UserTable.query.get(user_id)
            if not user:
                return False, "User not found."

            # Delete previous image on Cloudinary
            ProfileService.delete_old_image(user)

            # Upload directly to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder="profiles",
                transformation=[
                    {"width": 300, "height": 300, "crop": "fill", "gravity": "face"}
                ],
            )

            # Save full HTTPS URL in database
            user.image = upload_result.get("secure_url")

            # Store public_id if your model supports it
            if hasattr(user, "image_public_id"):
                user.image_public_id = upload_result.get("public_id")

            db.session.commit()
            return True, "Profile image updated successfully."

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(f"Upload Profile Image Error: {e}")
            return False, "Unable to upload profile image."
    # =========================================================
    # Remove Profile Image
    # =========================================================
    @staticmethod
    def remove_profile_image(user_id):

        # try:

        #     user = UserTable.query.get(user_id)

        #     if not user:

        #         return (
        #             False,
        #             "User not found."
        #         )

        #     # -----------------------------------------
        #     # Delete Physical Image
        #     # -----------------------------------------

        #     ProfileService.delete_old_image(user)

        #     # -----------------------------------------
        #     # Remove Database Path
        #     # -----------------------------------------

        #     user.image = None

        #     db.session.commit()

        #     return (
        #         True,
        #         "Profile image removed successfully."
        #     )

        # except Exception as e:

        #     db.session.rollback()

        #     current_app.logger.exception(
        #         f"Remove Profile Image Error: {e}"
        #     )

        #     return (
        #         False,
        #         "Unable to remove profile image."
        #     )
        try:
            user = UserTable.query.get(user_id)
            if not user:
                return False, "User not found."

            # Delete image from Cloudinary
            ProfileService.delete_old_image(user)

            # Reset user image field in DB
            user.image = None
            if hasattr(user, "image_public_id"):
                user.image_public_id = None

            db.session.commit()
            return True, "Profile image removed successfully."

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(f"Remove Profile Image Error: {e}")
            return False, "Unable to remove profile image."

    # =========================================================
    # Change Password
    # =========================================================
    @staticmethod
    def change_password(user_id, new_password):

        try:

            user = UserTable.query.get(user_id)

            if not user:
                return None

            user.set_password(new_password)

            db.session.commit()

            return user

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                f"Change Password Error: {e}"
            )

            return None