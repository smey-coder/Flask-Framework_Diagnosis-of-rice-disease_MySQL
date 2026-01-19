from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models.permission import PermissionTable
from app.models.role import RoleTable
from extensions import db
from app.forms.multi_checkbox_field import MultiCheckboxField

MODULE_CHOICES = [
    ("Users", "Users"),
    ("Roles", "Roles"),
    ("Products", "Products"),
    ("Orders", "Orders"),
    ("General", "General"),
    ("Permission", "Permission"),
    ("Fasts", "Fasts"),
    ("Rules", "Rules"),
]
class PermissionCreateForm(FlaskForm):
    
    code = StringField(
        "Code",
        validators=[DataRequired(), Length(min=2, max=64)],
        render_kw={"placeholder": "e.g., user.view"},
    )
    name = StringField(
        "Permission Name",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "e.g., create_user, edit_user, delete_user"},
    )
    module = SelectField(
        "Module",
        choices=MODULE_CHOICES,
        default="General",
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "What does this permission allow?"},
    )
    
    submit = SubmitField("Save")
    
    def validate_code(self, field):
        exists = db.session.scalar(
            db.select(PermissionTable).filter(PermissionTable.code == field.data)
        )
        if exists:
            raise ValidationError("This permission code already exists.")
        
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(PermissionTable).filter(PermissionTable.name == field.data)
        )
        if exists:
            raise ValidationError("This permission already exists.")

class PermissionEditForm(FlaskForm):
    
    code = StringField(
        "Code",
        validators=[DataRequired(), Length(min=2, max=64)],
        render_kw={"placeholder": "e.g., user.view"},
    )
    
    name = StringField(
        "Permission Name",
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    
    module = SelectField(
        "Module",
        choices=MODULE_CHOICES,
        default="General",
    )
    
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "What does this permission allow?"},
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_permission: PermissionTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_permission = original_permission
        
        if not self.is_submitted():
            self.module.data = original_permission.module
    def validate_code(self, field):
        if field.data != self.original_permission.code:
            exists = db.session.scalar(
                db.select(PermissionTable).filter(PermissionTable.code == field.data)
            )
            if exists:
                raise ValidationError("This permission code already exists.")
    
    def validate_name(self, field):
        if field.data != self.original_permission.name:
            exists = db.session.scalar(
                db.select(PermissionTable).filter(PermissionTable.name == field.data)
            )
            if exists:
                raise ValidationError("This permission already exists.")

class PermissionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")


def _role_choices():
    """Get all available roles for permission assignment."""
    return [
        (role.id, role.name)
        for role in db.session.scalars(
            db.select(RoleTable).order_by(RoleTable.name)
        )
    ]


class AssignPermissionToRoleForm(FlaskForm):
    """Form to assign permissions to roles."""
    role_id = SelectField(
        "Select Role",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    
    submit = SubmitField("Assign Permission")
    
    def __init__(self, permission: PermissionTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission = permission
        self.role_id.choices = _role_choices()
    
    def validate_role_id(self, field):
        """Check if role already has this permission."""
        role = db.session.get(RoleTable, field.data)
        if role and self.permission in role.permissions:
            raise ValidationError(f"Role '{role.name}' already has this permission.")


class RemovePermissionFromRoleForm(FlaskForm):
    """Form to remove permissions from roles."""
    role_id = SelectField(
        "Select Role",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    
    submit = SubmitField("Remove Permission")
    
    def __init__(self, permission: PermissionTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission = permission
        # Only show roles that have this permission
        roles_with_perm = db.session.scalars(
            db.select(RoleTable).filter(RoleTable.permissions.contains(permission))
        )
        self.role_id.choices = [(r.id, r.name) for r in roles_with_perm]


class BulkAssignPermissionsForm(FlaskForm):
    """Form to assign multiple permissions to a role."""
    role_id = SelectField(
        "Select Role",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    
    permission_ids = MultiCheckboxField(
        "Select Permissions",
        coerce=int,
    )
    
    submit = SubmitField("Assign Permissions")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id.choices = _role_choices()
        self.permission_ids.choices = [
            (perm.id, f"{perm.code} - {perm.name}")
            for perm in db.session.scalars(
                db.select(PermissionTable).order_by(PermissionTable.code)
            )
        ]
