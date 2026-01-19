from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

# Create user blueprint
user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="../../templates")

def user_required(f):
    """Decorator to ensure user has User role or no role restriction"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        # User role is default, so we allow access
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route("/dashboard", methods=["GET"])
@login_required
@user_required
def dashboard():
    """User dashboard page"""
    return render_template("user_page/dashboard.html", user=current_user)


@user_bp.route("/", methods=["GET"])
@login_required
@user_required
def index():
    """User index - redirects to dashboard"""
    return redirect(url_for("user.dashboard"))
