from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models.permission import PermissionTable
from extensions import db

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
