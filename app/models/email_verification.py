# app/models/email_verification.py
from datetime import datetime, timedelta
from extensions import db

class EmailVerification(db.Model):
    __tablename__ = "email_verifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_table.id"), nullable=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # 'register' or 'reset'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)

    def mark_used(self):
        self.is_used = True
        db.session.commit()

    @staticmethod
    def create(email, code, purpose="register", user_id=None, ttl_minutes=15):
        expires = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        ev = EmailVerification(email=email, code=code, purpose=purpose, user_id=user_id, expires_at=expires)
        db.session.add(ev)
        db.session.commit()
        return ev
