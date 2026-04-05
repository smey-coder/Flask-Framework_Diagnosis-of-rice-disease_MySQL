from collections import defaultdict
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import RoleTable, PermissionTable
from extensions import db
from app.forms.multi_checkbox_field import MultiCheckboxField

def _permission_choices():
    return [
        (perm.id, f"{perm.code} - {perm.name}")
        for perm in db.session.scalars(
            db.select(PermissionTable).order_by(PermissionTable.code)
        )
    ]
    
def _permissions_grouped_by_module():
    """
    Return  permissions grouped by module:
    {
        "Users": [Permissions Group, ...],
        } 
    """
    
    perms = list(
        db.session.scalars(
            db.select(PermissionTable).order_by(PermissionTable.module, PermissionTable.code
            )
        )
    )
    
    groupedd = defaultdict(list)
    for perm in perms:
        module = perm.module or "General"
        groupedd[module].append(perm)
        
    return dict(groupedd)

# Role forms
class RoleCreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Role name"},
    )
    description = StringField(
        "Description",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Short description (Optional)"},
    )
    permission_ids = MultiCheckboxField(
        "Permissions",
        coerce=int,
    )
    
    submit = SubmitField("Save")
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permissions_grouped_by_module()        
        
    # ---------- server-side uniqueness checks ---------
    
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(RoleTable).filter(RoleTable.name == field.data)
        )
        if exists:
            raise ValidationError("This name is already taken.")
        
        
# --------- edit form (password optional) -------------
class RoleEditForm(FlaskForm):
    name = StringField(
        "Name:",
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    
    description = TextAreaField("Description")
    
    permission_ids = MultiCheckboxField(
        "Permissions",
        coerce=int,
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_role: RoleTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_role = original_role
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permissions_grouped_by_module()
        
        if not self.is_submitted():
            # Pre-fill with current permissions
            self.permission_ids.data = [perm.id for perm in original_role.permissions]

    def validate_name(self, field):
        q = db.select(RoleTable).filter(
            RoleTable.name == field.data, 
            RoleTable.id != self.original_role.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This name is already taken.")


class RoleConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
    
