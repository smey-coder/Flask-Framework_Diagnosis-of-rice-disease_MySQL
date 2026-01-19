from typing import Optional,List
from extensions import db
from app.models.symptoms import SymptomsTable
from sqlalchemy import or_
from extensions import db

class SymptomService:
    @staticmethod
    def get_symptom_all() -> List[SymptomsTable]:
        """Retrieve all symptoms from the database."""
        return SymptomsTable.query.order_by(SymptomsTable.id.desc()).all()
    @staticmethod
    def get_symptom_by_id(symptom_id: int) -> Optional[SymptomsTable]:
        """Retrieve a symptom by its ID."""
        return db.session.get(SymptomsTable, symptom_id)
    @staticmethod
    def create_symptom(data: dict) -> SymptomsTable:
        symptom = SymptomsTable(
            symptom_name=data.get("symptom_name"),
            symptom_group=data.get("symptom_group"),
            description=data.get("description"),
            is_active=data.get("is_active", True),
        )
        db.session.add(symptom)
        db.session.commit()
        return symptom
    
    @staticmethod
    def update_symptom(symptom: SymptomsTable, data: dict) -> SymptomsTable:
        symptom.symptom_name = data.get("symptom_name", symptom.symptom_name)
        symptom.symptom_group = data.get("symptom_group", symptom.symptom_group)
        symptom.description = data.get("description", symptom.description)
        symptom.is_active = data.get("is_active", symptom.is_active)
        
        db.session.commit()
        return symptom
    
    @staticmethod
    def delete_symptom(symptom: SymptomsTable) -> None:
        db.session.delete(symptom)
        db.session.commit()
   