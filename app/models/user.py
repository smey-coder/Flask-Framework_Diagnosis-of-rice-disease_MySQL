from datetime import datetime,timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.associations import tbl_user_roles
class UserTable(UserMixin, db.Model):
    __tablename__ = "tbl_users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    #NEW: store only the hash, never plain text
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Note: match RoleTable.users

    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expire = db.Column(db.DateTime)

    
    roles = db.relationship("RoleTable", secondary=tbl_user_roles, back_populates="users")
    
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def set_reset_code(self, otp, minutes=5):
        self.reset_code = otp
        self.reset_code_expire = datetime.utcnow() + timedelta(minutes= minutes)

    def is_reset_code_valid(self, otp, minutes = 5):
        return(
            self.reset_code == otp
            and self.reset_code_expire
            and self.reset_code_expire >= datetime.utcnow()
        )
    
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
    
    def get_permission_code(self) -> set[str]:
        
        return {perm.code for role in self.roles for perm in role.permissions}
    
    def has_permission(self, permission_code: str) -> bool:
        return permission_code in self.get_permission_code()
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"
    