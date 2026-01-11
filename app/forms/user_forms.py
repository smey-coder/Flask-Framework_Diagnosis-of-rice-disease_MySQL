import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from config import Config
from extensions import db
from app.models.user import UserTable
from app.models.role import RoleTable

def strong_password(form, field):
    """"Requirement: min 8 chars, apper, lower, digit, special."""

    password = field.data or ""

    if not password:
        return
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")  
    
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")  
    
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
        raise ValidationError("Password must contain at least one special character.")
    
def _role_choices():
    """Return list of tuples for role select field."""
    return [
        (role.id, role.name)
        for role in db.session.scalars(
            db.select(RoleTable).order_by(RoleTable.name)
        )
    ]
class UserCreateForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Enter username"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "Enter email"},
    )
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
        render_kw={"placeholder": "Enter full name"},
    )
    is_active = BooleanField("Active", default=True)
    
    role_id = SelectField(
        "Role",
        coerce=int,
        choices=[],
        render_kw={"placeholder": "Select role"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(), 
            strong_password],
        render_kw={"placeholder": "Strong password"},
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ],
        render_kw={"placeholder": "Confirm password"},
    )
    
    submit = SubmitField("Save")
    
    # ---------- server-side uniqueness checks ---------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id.choices = _role_choices()
    
    def validate_username(self, field):
        exists = db.session.scalar(
            db.select(UserTable).filter(UserTable.username == field.data)
        )
        if exists:
            raise ValidationError("This username is already taken.")
        
    def validate_email(self, field):
        exists = db.session.scalar(
            db.select(UserTable).filter(UserTable.email == field.data)
        )
        if exists:
            raise ValidationError("This email is already taken.")
        
        
# --------- edit form (password optional) -------------
class UserEditForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Length(max=120)],
    )
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    is_active = BooleanField("Active")
    
    # -------- optional password - only change if filled
    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()],
    )
    password = PasswordField(
        "New password (leave blank to keep current)",
        validators=[strong_password],
        render_kw={"placeholder": "New strong password (optional)"},
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[EqualTo("password", message="Passwords must match.")]
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user
        self.role_id.choices = _role_choices()

        if not self.is_submitted():
            if original_user.roles:
                self.role_id.data = original_user.roles[0].id
            else:
                self.role_id.data = None
        
    def validate_username(self, field):
        q = db.select(UserTable).filter(
            UserTable.username == field.data,
            UserTable.id != self.original_user.id
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        q = db.select(UserTable).filter(
            UserTable.email == field.data,
            UserTable.id != self.original_user.id
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This email is already registered.")

class UserConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
    

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your username"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your password"},
    )
    is_active = BooleanField("Remember me", default=True)
    submit = SubmitField("Login")