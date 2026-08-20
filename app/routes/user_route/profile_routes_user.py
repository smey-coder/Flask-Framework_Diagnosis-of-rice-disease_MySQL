from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.services.profile_service import ProfileService

from app.decorators.access import role_required, permission_required

profile_user_bp = Blueprint("user_profile",__name__,url_prefix="/user/profile", template_folder="../../templates")
# =========================================================
# PROFILE
# =========================================================

@profile_user_bp.route("/")
@login_required
@role_required("User")
@permission_required("VIEW_PROFILE")
def index():

    try:

        user = ProfileService.get_profile(
            current_user.id
        )

        if not user:
            flash(
                "User profile not found.",
                "danger"
            )

            return redirect(
                url_for("user.dashboard")
            )

        return render_template(
            "user_page/profiles/index.html",
            user=user
        )

    except Exception as e:

        print(
            f"Profile Index Error: {e}"
        )

        flash(
            "Unable to load your profile.",
            "danger"
        )

        return redirect(
            url_for("user.dashboard")
        )


# =========================================================
# UPDATE PROFILE
# =========================================================

@profile_user_bp.route("/update",methods=["POST"])
@login_required
@role_required("User")
@permission_required("UPDATE_PROFILE")
def update():

    try:

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        if not full_name:
            flash(
                "Full name is required.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        if not email:
            flash(
                "Email is required.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        ProfileService.update_profile(
            current_user.id,
            {
                "full_name": full_name,
                "email": email
            }
        )

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("user_profile.index")
        )

    except Exception as e:

        print(
            f"Profile Update Error: {e}"
        )

        flash(
            "Unable to update profile.",
            "danger"
        )

        return redirect(
            url_for("user_profile.index")
        )

# =========================================================
# UPLOAD / UPDATE PROFILE IMAGE
# =========================================================

# =========================================================
# UPLOAD / UPDATE PROFILE IMAGE
# =========================================================

@profile_user_bp.route(
    "/upload-image",
    methods=["POST"]
)
@login_required
@role_required("User")
@permission_required("UPDATE_PROFILE")
def upload_image():

    try:

        # =========================================
        # Get uploaded file
        # =========================================

        image = request.files.get("image")

        current_app.logger.info(
            f"Upload image request - "
            f"user_id={current_user.id}, "
            f"filename={image.filename if image else None}"
        )

        # =========================================
        # Check file
        # =========================================

        if image is None:
            flash(
                "No image was uploaded.",
                "warning"
            )

            return redirect(
                url_for("user_profile.index")
            )

        if not image.filename:
            flash(
                "Please select an image.",
                "warning"
            )

            return redirect(
                url_for("user_profile.index")
            )

        # =========================================
        # Check extension
        # =========================================

        if not ProfileService.allowed_file(
            image.filename
        ):

            flash(
                "Invalid image format. "
                "Only JPG, JPEG, PNG and WEBP are allowed.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        # =========================================
        # Upload through Service
        # =========================================

        success, message = ProfileService.upload_profile_image(
            current_user.id,
            image
        )

        # =========================================
        # Upload failed
        # =========================================

        if not success:

            flash(
                message,
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        # =========================================
        # Upload success
        # =========================================

        flash(
            message,
            "success"
        )

        return redirect(
            url_for("user_profile.index")
        )

    except Exception as e:

        current_app.logger.exception(
            "User Profile Image Upload Error"
        )

        flash(
            "Unable to update profile image.",
            "danger"
        )

        return redirect(
            url_for("user_profile.index")
        )

# =========================================================
# REMOVE PROFILE IMAGE
# =========================================================

@profile_user_bp.route(
    "/remove-image",
    methods=["POST"]
)
@login_required
@role_required("User")
@permission_required("UPDATE_PROFILE")
def remove_image():

    try:

        user = ProfileService.remove_profile_image(
            current_user.id
        )

        if not user:

            flash(
                "User profile not found.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        flash(
            "Profile image removed successfully.",
            "success"
        )

        return redirect(
            url_for("user_profile.index")
        )

    except Exception as e:

        current_app.logger.exception(
            f"Remove Profile Image Error: {e}"
        )

        flash(
            "Unable to remove profile image.",
            "danger"
        )

        return redirect(
            url_for("user_profile.index")
        )

# =========================================================
# CHANGE PASSWORD
# =========================================================

@profile_user_bp.route("/change-password",methods=["POST"])
@login_required
@role_required("User")
@permission_required("CHANGE_PASSWORD")
def change_password():

    try:

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -----------------------------------------
        # Validation
        # -----------------------------------------

        if not current_password:
            flash(
                "Current password is required.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        if not new_password:
            flash(
                "New password is required.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        if new_password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        # -----------------------------------------
        # Verify current password
        # -----------------------------------------

        if not current_user.check_password(
            current_password
        ):
            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("user_profile.index")
            )

        # -----------------------------------------
        # Update password
        # -----------------------------------------

        ProfileService.change_password(
            current_user.id,
            new_password
        )

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("user_profile.index")
        )

    except Exception as e:

        print(
            f"Change Password Error: {e}"
        )

        flash(
            "Unable to change password.",
            "danger"
        )

        return redirect(
            url_for("user_profile.index")
        )