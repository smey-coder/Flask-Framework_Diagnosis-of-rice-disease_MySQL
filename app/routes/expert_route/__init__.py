from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

# Create expert blueprint
expert_bp = Blueprint("expert", __name__, url_prefix="/expert", template_folder="../../templates")

def expert_required(f):
    """Decorator to ensure user has Expert role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.has_role("Expert"):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@expert_bp.route("/dashboard", methods=["GET"])
@login_required
@expert_required
def dashboard():
    """Expert dashboard page"""
    return render_template("expert_page/dashboard.html", user=current_user)


@expert_bp.route("/", methods=["GET"])
@login_required
@expert_required
def index():
    """Expert index - redirects to dashboard"""
    return redirect(url_for("expert.dashboard"))
