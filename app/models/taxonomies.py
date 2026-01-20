from extensions import db
from datetime import datetime

class TaxonomyTable(db.Model):
    __tablename__ = 'tbl_taxonomies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)