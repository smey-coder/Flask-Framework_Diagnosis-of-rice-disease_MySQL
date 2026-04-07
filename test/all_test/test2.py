# Example: check in Python shell
from app.models.treatments import TreatmentTable

treatments = TreatmentTable.query.filter_by(disease_id=1, is_active=True).all()
print(treatments)
