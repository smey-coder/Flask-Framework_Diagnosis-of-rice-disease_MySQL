from typing import Optional
import random
from app.models.user import UserTable
from extensions import db, mail
from werkzeug.security import generate_password_hash
from flask_mail import Message


class AuthService:
    """Authentication & password recovery service"""

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[UserTable]:
        user = UserTable.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    # ---------- FORGOT PASSWORD ----------
    @staticmethod
    def send_reset_code(email: str) -> bool:
        user = UserTable.query.filter_by(email=email, is_active=True).first()
        if not user:
            return False

        otp = str(random.randint(100000, 999999))
        user.set_reset_code(otp)
        db.session.commit()

        msg = Message(
            subject="Password Reset Verification Code",
            recipients=[email],
            body=f"Your OTP code is: {otp}\nThis code expires in 5 minutes."
        )
        mail.send(msg)

        return True

    # ---------- VERIFY OTP ----------
    @staticmethod
    def verify_reset_code(email: str, otp: str) -> bool:
        user = UserTable.query.filter_by(email=email).first()
        if not user:
            return False

        return user.is_reset_code_valid(otp)

    # ---------- RESET PASSWORD ----------
    @staticmethod
    def reset_password(email: str, new_password: str) -> bool:
        user = UserTable.query.filter_by(email=email).first()
        if not user:
            return False

        user.password_hash = generate_password_hash(new_password)
        user.reset_code = None
        user.reset_code_expire = None
        db.session.commit()
        return True
