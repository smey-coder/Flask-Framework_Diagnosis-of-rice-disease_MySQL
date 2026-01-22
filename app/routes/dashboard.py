from flask import Blueprint, render_template
from flask_login import login_required

from app.models.user import UserTable
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable

count_bp = Blueprint("admin", __name__, url_prefix="/admin")

@count_bp.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "users": UserTable.query.count(),
        "diseases": DiseaseTable.query.count(),
        "symptoms": SymptomsTable.query.count(),
        "rules": RulesTable.query.count(),
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats
    )
