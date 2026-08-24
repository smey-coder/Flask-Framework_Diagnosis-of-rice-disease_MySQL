from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class HarvestForm(FlaskForm):
    # Cascading Dropdowns
    farm_id = SelectField('កសិដ្ឋាន (Farm)', coerce=int, validators=[DataRequired()])
    field_id = SelectField('ក្បាលដី/ស្រែ (Field)', coerce=int, validators=[DataRequired()])
    field_crop_id = SelectField('ដំណាំក្នុងស្រែ (Field Crop)', coerce=int, validators=[DataRequired()])
    harvest_date = DateField('Harvest Date (កាលបរិច្ឆេទ)', validators=[DataRequired()])
    quality_grade = SelectField(
        'Quality Grade (គុណភាព)',
        choices=[
            ('Grade A (Premium)', 'Grade A (Premium)'),
            ('Grade B (Standard)', 'Grade B (Standard)'),
            ('Grade C (Low)', 'Grade C (Low)')
        ],
        validators=[DataRequired()]
    )
    
    # ជម្រើសរូបិយប័ណ្ណ
    currency = SelectField(
        'Currency (រូបិយប័ណ្ណ)',
        choices=[('USD', 'USD ($)'), ('KHR', 'KHR (៛)')],
        default='USD'
    )
    exchange_rate = FloatField('Exchange Rate (1 USD = ? KHR)', default=4046.0)

    quantity_tons = FloatField('Quantity / Tons (បរិមាណ)', validators=[DataRequired(), NumberRange(min=0.01)])
    price_per_ton = FloatField('Price / Ton (តម្លៃ/តោន)', validators=[DataRequired(), NumberRange(min=0.0)])
    total_cost = FloatField('Total Cost (ចំណាយសរុប)', validators=[DataRequired(), NumberRange(min=0.0)])
    submit = SubmitField('💾 រក្សាទុក និងមើលរបាយការណ៍')