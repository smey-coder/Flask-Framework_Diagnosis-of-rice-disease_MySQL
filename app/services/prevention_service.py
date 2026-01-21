from typing import List, Optional
from extensions import db
from app.models.preventions import PreventionTable
from app.models.diseases import DiseaseTable
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PreventionService:
    @staticmethod
    def get_all(active_only: bool = False) -> List[PreventionTable]:
        query = PreventionTable.query.order_by(PreventionTable.id.desc())
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_by_id(prevention_id: int) -> Optional[PreventionTable]:
        return PreventionTable.query.get_or_404(prevention_id)

    @staticmethod
    def create(data: dict, image_file=None) -> PreventionTable:
        filename = ""
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(current_app.root_path, 'static/images/preventions')
            os.makedirs(save_path, exist_ok=True)
            image_file.save(os.path.join(save_path, filename))
        else:
            raise ValueError("Image is required and must be valid.")

        # Check duplicates
        duplicate = PreventionTable.query.filter_by(
            disease_id=data.get("disease_id"),
            prevention_type=data.get("prevention_type")
        ).first()
        if duplicate:
            raise ValueError(f"A prevention of type '{data.get('prevention_type')}' already exists for this disease.")

        prevention = PreventionTable(
            disease_id=data.get("disease_id"),
            prevention_type=data.get("prevention_type"),
            description=data.get("description", ""),
            image=filename,
            is_active=data.get("is_active", True)
        )

        try:
            db.session.add(prevention)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        return prevention

    @staticmethod
    def update(prevention: PreventionTable, data: dict, image_file=None) -> PreventionTable:
        # Check duplicates
        duplicate = PreventionTable.query.filter(
            PreventionTable.id != prevention.id,
            PreventionTable.disease_id == data.get("disease_id"),
            PreventionTable.prevention_type == data.get("prevention_type")
        ).first()
        if duplicate:
            raise ValueError(f"A prevention of type '{data.get('prevention_type')}' already exists for this disease.")

        # Handle image update
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(current_app.root_path, 'static/images/preventions')
            os.makedirs(save_path, exist_ok=True)
            image_file.save(os.path.join(save_path, filename))
            prevention.image = filename  # update image

        prevention.disease_id = data.get("disease_id", prevention.disease_id)
        prevention.prevention_type = data.get("prevention_type", prevention.prevention_type)
        prevention.description = data.get("description", prevention.description)
        prevention.is_active = data.get("is_active", prevention.is_active)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        return prevention

    @staticmethod
    def delete(prevention: PreventionTable):
        try:
            db.session.delete(prevention)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")
