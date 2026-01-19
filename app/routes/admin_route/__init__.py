from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

# Create admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../../templates")

def admin_required(f):
    """Decorator to ensure user has Admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.has_role("Admin"):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    """Admin dashboard page"""
    return render_template("admin_page/dashboard.html", user=current_user)


@admin_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    """Admin index - redirects to dashboard"""
    return redirect(url_for("admin.dashboard"))
