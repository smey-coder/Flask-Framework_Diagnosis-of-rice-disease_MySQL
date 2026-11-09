from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
# from decorators import require_permission, require_role, active_user_required
from app.models.user import UserTable
from app.models.role import RoleTable
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from extensions import csrf, db, oauth
from app.decorators.access import permission_required, role_required
from sqlalchemy import func

import re

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _login_and_redirect(user, remember=False):
    if not user.is_active:
        flash("Your account is inactive. Please contact administrator.", "warning")
        return redirect(url_for("auth.login"))

    if user.has_role("Admin"):
        destination = "admin.dashboard"
    elif user.has_role("Expert"):
        destination = "expert.dashboard"
    elif user.has_role("User"):
        destination = "user.dashboard"
    else:
        flash("No role assigned. Contact administrator.", "warning")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    flash(f"Welcome back, {user.full_name}!", "success")
    return redirect(url_for(destination))


def _new_google_username(email):
    base = re.sub(r"[^A-Za-z0-9_.-]", "", email.split("@", 1)[0])[:70] or "google"
    suffix = 1
    username = base
    while UserTable.query.filter_by(username=username).first():
        suffix_text = str(suffix)
        username = f"{base[:80 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return username


#pubblic Login and rigister
# ===================== LOGIN =====================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            remember = True if request.form.get("remember") else False 

            user = UserTable.query.filter_by(username=username).first()
        
            if not user or not user.check_password(password):
                flash("Invalid username or password.", "danger")
                return redirect(url_for("auth.login"))
            return _login_and_redirect(user, remember=remember)

        return render_template("auth/login.html")
    except Exception as e:
        current_app.logger.exception("Login Error")
        flash("Something went wrong while signing in. Please try again.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/google")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        current_app.logger.error("Google sign-in requested without configured OAuth credentials.")
        flash("Google sign-in is not configured. Please use your username and password.", "warning")
        return redirect(url_for("auth.login"))

    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI") or url_for(
        "auth.google_callback", _external=True
    )
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        profile = token.get("userinfo") or oauth.google.userinfo()
    except Exception:
        current_app.logger.exception("Google OAuth callback failed.")
        flash("Google sign-in failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    google_id = profile.get("sub")
    email = (profile.get("email") or "").strip().lower()
    if not google_id or not email or profile.get("email_verified") is not True:
        flash("Google did not provide a verified email address.", "danger")
        return redirect(url_for("auth.login"))

    try:
        user = AuthService.get_user_by_google_id(google_id)
        if user is None:
            user = UserTable.query.filter(func.lower(UserTable.email) == email).first()

            if user and user.google_id and user.google_id != google_id:
                flash("This email is already linked to a different Google account.", "danger")
                return redirect(url_for("auth.login"))

            if user is None:
                user_role = RoleTable.query.filter_by(name="User").first()
                if user_role is None:
                    current_app.logger.error("Cannot create Google account: User role is missing.")
                    flash("Registration is temporarily unavailable. Please contact the administrator.", "danger")
                    return redirect(url_for("auth.register"))

                full_name = (profile.get("name") or email.split("@", 1)[0]).strip()[:80]
                user = UserService.create_google_user(
                    data={
                        "username": _new_google_username(email),
                        "email": email,
                        "full_name": full_name or email,
                        "image": profile.get("picture"),
                    },
                    google_id=google_id,
                    role_id=user_role.id,
                )
            else:
                user.google_id = google_id
                if user.password_hash is None:
                    user.auth_provider = "google"
                db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unable to create or link Google account.")
        flash("Something went wrong while signing in with Google. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    return _login_and_redirect(user)
# ===================== REGISTER =====================
@auth_bp.route("/register", methods=["GET", "POST"])
@csrf.exempt
def register():
    try:
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            full_name = request.form.get("full_name", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            errors = []

            if not username:
                errors.append("Username is required.")
            if not email:
                errors.append("Email is required.")
            if not full_name:
                errors.append("Full name is required.")
            if not password:
                errors.append("Password is required.")
            if password != confirm_password:
                errors.append("Passwords do not match.")

            if UserTable.query.filter_by(username=username).first():
                errors.append("Username already exists.")
            if UserTable.query.filter_by(email=email).first():
                errors.append("Email already registered.")

            if errors:
                for e in errors:
                    flash(e, "danger")
                return render_template("auth/register.html", **request.form)

            # default_role = RoleTable.query.filter_by(name="User").first()
            # default_role_id = default_role.id if default_role else None

            new_user = UserService.create_user(
                data={
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "is_active": True,
                },
                password=password,
                # role_id=default_role_id,
            )
            user_role = RoleTable.query.filter_by(name="User").first()
            if user_role:
                new_user.roles.append(user_role)
                db.session.commit()
        
            flash("Your account has been created successfully. Please log in to continue.", "success")
            return redirect(url_for("auth.login"))

        return render_template("auth/register.html")
    except Exception:
            # Rollback database transaction
            db.session.rollback()
            # Log real error to server console/log
            current_app.logger.exception(
                "Registration Error"
            )
            # User-friendly message
            flash(
                "Something went wrong while creating your account. "
                "Please try again.",
                "danger"
            )
    
            return render_template(
                "auth/register.html",
                username=request.form.get("username", ""),
                email=request.form.get("email", ""),
                full_name=request.form.get("full_name", "")
            )


# ===================== LOGOUT =====================
@auth_bp.route("/logout")
@login_required
@role_required("Admin", "Expert", "User")
def logout():
    try:
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("auth.login"))
    except Exception as e:
        current_app.logger.exception("Logout Error")
        flash("Something went wrong while logging out.","danger")
        return redirect(url_for("auth.login"))


# ===================== FORGOT PASSWORD =====================
@auth_bp.route("/forget-password", methods=["GET", "POST"])
@csrf.exempt
def forget_password():
    try:
        if request.method == "POST":
            email = request.form.get("email")

            if not email:
                flash("Email is required", "warning")
                return redirect(request.url)

            if AuthService.send_reset_code(email):
                flash("OTP sent to your email", "success")
                return redirect(url_for("auth.verify_email", email=email))

            flash("Email not found", "danger")

        return render_template("auth/forget_password.html")

    except Exception as e:
        current_app.logger.error(f"Forget Password Error: {str(e)}")
        flash("Something went wrong. Please try again.", "danger")
        return redirect(request.url)


# ===================== VERIFY EMAIL =====================
@auth_bp.route("/verify-email", methods=["GET", "POST"])
@csrf.exempt
def verify_email():
    try:
        email = request.args.get("email")
        if not email:
            flash("Invalid request", "danger")
            return redirect(url_for("auth.forget_password"))
        if request.method == "POST":
            otp = request.form.get("otp")

            if not otp:
                flash("OTP is required", "warning")
                return redirect(request.url)

            if AuthService.verify_reset_code(email, otp):
                return redirect(url_for("auth.reset_password", email=email))

            flash("Invalid or expired OTP", "danger")

        return render_template("auth/verify_email.html", email=email)

    except Exception as e:
        current_app.logger.error(f"Verify Email Error: {str(e)}")
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("auth.forget_password"))


# ===================== RESET PASSWORD =====================
@auth_bp.route("/reset-password", methods=["GET", "POST"])
@csrf.exempt
def reset_password():
    try:
        email = request.args.get("email")

        if not email:
            flash("Invalid request", "danger")
            return redirect(url_for("auth.forget_password"))

        if request.method == "POST":
            password = request.form.get("password")
            confirm = request.form.get("confirm_password")

            if not password or not confirm:
                flash("All fields are required", "warning")
                return redirect(request.url)

            if password != confirm:
                flash("Passwords do not match", "danger")
                return redirect(request.url)

            AuthService.reset_password(email, password)

            flash("Password reset successful", "success")
            return redirect(url_for("auth.login"))

        return render_template("auth/reset_password.html", email=email)

    except Exception as e:
        current_app.logger.error(f"Reset Password Error: {str(e)}")
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("auth.forget_password"))