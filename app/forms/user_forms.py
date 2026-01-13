import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from extensions import db
from app.models.user import UserTable
from app.models.role import RoleTable

# ------------------ Password strength validator ------------------
def strong_password(form, field):
    """Requirement: min 8 chars, uppercase, lowercase, digit, special."""
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


# ------------------ Role select choices ------------------
def _role_choices():
    return [
        (role.id, role.name)
        for role in db.session.scalars(db.select(RoleTable).order_by(RoleTable.name))
    ]


# ------------------ User Create Form ------------------
class UserCreateForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    is_active = BooleanField("Active", default=True)
    role_id = SelectField("Role", coerce=int, choices=[])
    password = PasswordField("Password", validators=[DataRequired(), strong_password])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id.choices = _role_choices()

    def validate_username(self, field):
        if db.session.scalar(db.select(UserTable).filter(UserTable.username == field.data)):
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        if db.session.scalar(db.select(UserTable).filter(UserTable.email == field.data)):
            raise ValidationError("This email is already taken.")


# ------------------ User Edit Form ------------------
class UserEditForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    is_active = BooleanField("Active")
    role_id = SelectField("Role", coerce=int, validators=[DataRequired()])
    password = PasswordField("New Password (leave blank to keep current)", validators=[strong_password])
    confirm_password = PasswordField("Confirm New Password", validators=[EqualTo("password")])
    submit = SubmitField("Update")

    def __init__(self, original_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user
        self.role_id.choices = _role_choices()
        if not self.is_submitted() and original_user.roles:
            self.role_id.data = original_user.roles[0].id

    def validate_username(self, field):
        if db.session.scalar(db.select(UserTable).filter(UserTable.username == field.data, UserTable.id != self.original_user.id)):
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        if db.session.scalar(db.select(UserTable).filter(UserTable.email == field.data, UserTable.id != self.original_user.id)):
            raise ValidationError("This email is already registered.")


# ------------------ User Confirm Delete Form ------------------
class UserConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")


# ------------------ Login Form ------------------
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me", default=True)
    submit = SubmitField("Login")


# ------------------ Register Form ------------------
# class RegisterForm(FlaskForm):
#     username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
#     email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
#     full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
#     password = PasswordField("Password", validators=[DataRequired(), strong_password])
#     confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
#     submit = SubmitField("Register")

#     def validate_username(self, field):
#         if db.session.scalar(db.select(UserTable).filter(UserTable.username == field.data)):
#             raise ValidationError("This username is already taken.")

#     def validate_email(self, field):
#         if db.session.scalar(db.select(UserTable).filter(UserTable.email == field.data)):
#             raise ValidationError("This email is already taken.")


# # ------------------ Forget Password Form ------------------
# class ForgetPasswordForm(FlaskForm):
#     email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
#     submit = SubmitField("Send OTP")


# # ------------------ OTP Verification Form ------------------
# class OTPForm(FlaskForm):
#     otp = StringField("OTP", validators=[DataRequired(), Length(min=6, max=6)])
#     submit = SubmitField("Verify")


# # ------------------ Reset Password Form ------------------
# class ResetPasswordForm(FlaskForm):
#     password = PasswordField("New Password", validators=[DataRequired(), strong_password])
#     confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("password")])
#     submit = SubmitField("Reset Password")
