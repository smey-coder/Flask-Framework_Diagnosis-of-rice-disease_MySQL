from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.diseases import DiseaseTable
from app.models.user import UserTable

class FeedbackTable(UserMixin, db.Model):
    __tablename__ ="tbl_feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey(DiseaseTable.id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(UserTable.id), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Feedback {self.id}>"