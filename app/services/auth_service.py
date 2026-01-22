from typing import Optional
import random
from app.models.user import UserTable
from extensions import db, mail
from werkzeug.security import generate_password_hash
from flask_mail import Message
from app.services.audit_service import log_audit


class AuthService:
    """Authentication & password recovery service"""

    # ===================== AUTHENTICATE =====================
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[UserTable]:
        user = UserTable.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    # ===================== FORGOT PASSWORD =====================
    @staticmethod
    def send_reset_code(email: str) -> bool:
        """Generate and send OTP code to user email"""
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

    # ===================== VERIFY OTP =====================
    @staticmethod
    def verify_reset_code(email: str, otp: str) -> bool:
        """Verify OTP code for password reset"""
        user = UserTable.query.filter_by(email=email).first()
        if not user:
            return False
        return user.is_reset_code_valid(otp)

    # ===================== RESET PASSWORD =====================
    @staticmethod
    def reset_password(email: str, new_password: str) -> bool:
        """Reset user password and log the action"""
        user = UserTable.query.filter_by(email=email).first()
        if not user:
            return False

        # Before snapshot for audit
        before_data = {
            "password_hash": "********",
            "reset_code": user.reset_code,
            "reset_code_expire": str(user.reset_code_expire)
        }

        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.reset_code = None
        user.reset_code_expire = None
        db.session.commit()

        # After snapshot for audit
        after_data = {
            "password_hash": "********",
            "reset_code": None,
            "reset_code_expire": None
        }

        # ✅ Audit log for password reset
        log_audit(
            action="RESET_PASSWORD",
            table_name="users",
            record_id=user.id,
            before_data=before_data,
            after_data=after_data
        )

        return True
