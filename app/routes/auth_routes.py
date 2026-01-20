from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required
from app.models.user import UserTable
from app.models.role import RoleTable
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from extensions import csrf, db
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")




# ===================== LOGIN =====================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = UserTable.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account is inactive. Please contact administrator.", "warning")
                return redirect(url_for("auth.login"))

            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            
            # Role-based redirection
            if user.has_role("Admin"):
                return redirect(url_for("admin.dashboard"))
            elif user.has_role("Expert"):
                return redirect(url_for("expert.dashboard"))
            elif user.has_role("User"):
                return redirect(url_for("user.dashboard"))
            
            flash("No role assigned. Contact administrator.", "warning")
            return redirect(url_for("auth.login"))
                
            
        flash("Invalid username or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


# ===================== REGISTER =====================
@auth_bp.route("/register", methods=["GET", "POST"])
@csrf.exempt
def register():
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

    
        flash("Account created successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ===================== LOGOUT =====================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ===================== FORGOT PASSWORD =====================
@auth_bp.route("/forget-password", methods=["GET", "POST"])
@csrf.exempt
def forget_password():
    if request.method == "POST":
        email = request.form.get("email")
        if AuthService.send_reset_code(email):
            flash("OTP sent to your email", "success")
            return redirect(url_for("auth.verify_email", email=email))
        flash("Email not found", "danger")
    return render_template("auth/forget_password.html")

@auth_bp.route("/verify-email", methods=["GET", "POST"])
@csrf.exempt
def verify_email():
    email = request.args.get("email")
    if request.method == "POST":
        otp = request.form.get("otp")
        if AuthService.verify_reset_code(email, otp):
            return redirect(url_for("auth.reset_password", email=email))
        flash("Invalid or expired OTP", "danger")
    return render_template("auth/verify_email.html", email=email)

@auth_bp.route("/reset-password", methods=["GET", "POST"])
@csrf.exempt
def reset_password():
    email = request.args.get("email")
    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        if password != confirm:
            flash("Passwords do not match", "danger")
        else:
            AuthService.reset_password(email, password)
            flash("Password reset successful", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", email=email)