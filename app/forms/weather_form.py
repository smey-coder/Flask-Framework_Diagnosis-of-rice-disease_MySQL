from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

# Cambodia cities with their names for OpenWeatherMap API
CAMBODIA_CITIES = [
    ('Phnom Penh', 'Phnom Penh'),
    ('Siem Reap', 'Siem Reap'),
    ('Battambang', 'Battambang'),
    ('Sihanoukville', 'Sihanoukville'),
    ('Kampong Cham', 'Kampong Cham'),
    ('Kampong Speu', 'Kampong Speu'),
    ('Kampong Thom', 'Kampong Thom'),
    ('Kandal', 'Kandal'),
    ('Takeo', 'Takeo'),
    ('Prey Veng', 'Prey Veng'),
    ('Kampot', 'Kampot'),
    ('Kratie', 'Kratie'),
    ('Banteay Meanchey', 'Banteay Meanchey'),
    ('Pursat', 'Pursat'),
    ('Oddar Meanchey', 'Oddar Meanchey'),
    ('Kep', 'Kep'),
    ('Mondulkiri', 'Mondulkiri'),
    ('Ratanakiri', 'Ratanakiri'),
    ('Stung Treng', 'Stung Treng'),
    ('Svay Rieng', 'Svay Rieng'),
]

class CitySearchForm(FlaskForm):
    city = SelectField(
        'Select City in Cambodia',
        choices=CAMBODIA_CITIES,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    submit = SubmitField('Show Weather')