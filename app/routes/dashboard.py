from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models.user import UserTable
from app.models.diseases import DiseaseTable
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.forms.weather_form import CitySearchForm
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

    form = CitySearchForm()
    weather_data = None

    # Load default weather for Phnom Penh if no form submission
    if not form.validate_on_submit():
        weather_data = WeatherService.get_weather("Phnom Penh")

    if form.validate_on_submit():
        weather_data = WeatherService.get_weather(form.city.data)

    return render_template(
        "admin_page/dashboard.html",
        stats=stats,
        form=form,
        selected_city_weather=weather_data  # Changed variable name to match template
    )
