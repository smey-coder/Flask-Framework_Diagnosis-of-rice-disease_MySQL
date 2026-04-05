from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models.user import UserTable
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.forms.weather_form import WeatherForm
from app.services.weather_service import WeatherService

count_bp = Blueprint("admin", __name__, url_prefix="/admin")

@count_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    stats = {
        "users": UserTable.query.count(),
        "diseases": DiseaseTable.query.count(),
        "symptoms": SymptomsTable.query.count(),
        "rules": RulesTable.query.count(),
    }

    form = WeatherForm()
    weather_data = None

    if form.validate_on_submit():
        weather_data = WeatherService.get_weather(form.city.data, form.country.data)

    return render_template(
        "admin_page/dashboard.html",
        stats=stats,
        form=form,
        weather_data=weather_data
    )
