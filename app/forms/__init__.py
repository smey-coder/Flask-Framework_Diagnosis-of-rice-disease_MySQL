from app.forms.user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from app.forms.role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from app.forms.permission_forms import PermissionCreateForm, PermissionEditForm, PermissionConfirmDeleteForm
from app.forms.diagnosis_form import DiagnosisForm
from app.forms.weather_form import CitySearchForm
from app.forms.diseases_forms import DiseaseCreateForm, DiseaseEditForm, DiseaseConfirmDeleteForm, DiseaseSearchForm
__all__ = [
    "UserCreateForm",
    "UserEditForm",
    "UserConfirmDeleteForm",
    "RoleCreateForm",
    "RoleEditForm",
    "RoleConfirmDeleteForm",
    "PermissionCreateForm",
    "PermissionEditForm",
    "PermissionConfirmDeleteForm",
    "DiagnosisForm",
    "CitySearchForm",
    "DiseaseCreateForm",
    "DiseaseEditForm",
    "DiseaseConfirmDeleteForm",
    "DiseaseSearchForm",
    # "CitySearchForm"
]