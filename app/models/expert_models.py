from extensions import db
from datetime import datetime

# --- Model សម្រាប់ Facts (ចំណេះដឹង/ការពិត) ---
class FactTable(db.Model):
    __tablename__ = 'tbl_facts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Model សម្រាប់ Taxonomies (ការចាត់ថ្នាក់) ---
class TaxonomyTable(db.Model):
    __tablename__ = 'tbl_taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=False) # e.g., Family, Genus, Order
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)