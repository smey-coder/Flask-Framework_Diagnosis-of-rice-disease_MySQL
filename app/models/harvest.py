from datetime import datetime
from extensions import db

class Harvest(db.Model):
    __tablename__ = 'tbl_harvests'

    id = db.Column(db.Integer, primary_key=True)
    # Links directly to Field Crop
    field_crop_id = db.Column(db.Integer, db.ForeignKey('tbl_field_crops.id', ondelete='CASCADE'), nullable=False)

    harvest_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quantity_tons = db.Column(db.Float, nullable=False, default=0.0)
    quality_grade = db.Column(db.String(50), nullable=False)
    # ព័ត៌មានលុយ និងអត្រាប្តូរប្រាក់
    currency = db.Column(db.String(10), nullable=False, default='USD') # USD ឬ KHR
    exchange_rate = db.Column(db.Float, nullable=False, default=4046.0) # 1 USD = 4046 KHR
    price_per_ton = db.Column(db.Float, nullable=False, default=0.0)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    total_revenue = db.Column(db.Float, nullable=False, default=0.0)
    net_profit = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    farm = db.relationship('FarmTable', backref=db.backref('harvests', lazy=True, cascade='all, delete-orphan'))
    # Relationship to Field Crop
    field_crop = db.relationship('FieldCropTable', backref=db.backref('harvests', lazy=True, cascade='all, delete-orphan'))

    # Helper properties to traverse relationships up to Farm
    @property
    def field(self):
        """Access FieldTable via FieldCrop"""
        return self.field_crop.field if self.field_crop else None

    @property
    def farm(self):
        """Access FarmTable via Field -> FieldCrop"""
        return self.field_crop.field.farm if (self.field_crop and self.field_crop.field) else None

    @property
    def rice_variety(self):
        """Access RiceVarietyTable via FieldCrop"""
        return self.field_crop.rice_variety if self.field_crop else None