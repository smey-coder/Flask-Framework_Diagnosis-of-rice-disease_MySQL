from extensions import db
from app.models.diseases import DiseaseTable
from sqlalchemy import or_


class DiseaseService:
    """Service layer for disease-related operations"""
    
    @staticmethod
    def get_disease_all(page=1, per_page=10):
        """Get all diseases with pagination"""
        return db.paginate(
            db.select(DiseaseTable).order_by(DiseaseTable.id.desc()),
            page=page,
            per_page=per_page
        )
    
    @staticmethod
    def get_disease_by_id(disease_id: int):
        """Get a disease by ID"""
        return db.session.get(DiseaseTable, disease_id)
    
    @staticmethod
    def search_diseases(disease_name=None, disease_type=None, severity_level=None, page=1, per_page=10):
        """Search and filter diseases"""
        query = db.select(DiseaseTable)
        
        if disease_name:
            query = query.where(DiseaseTable.disease_name.ilike(f"%{disease_name}%"))
        
        if disease_type:
            query = query.where(DiseaseTable.disease_type == disease_type)
        
        if severity_level:
            query = query.where(DiseaseTable.severity_level == severity_level)
        
        query = query.order_by(DiseaseTable.id.desc())
        
        return db.paginate(query, page=page, per_page=per_page)
    
    @staticmethod
    def create_disease(data: dict):
        """Create a new disease
        
        Args:
            data: Dictionary containing disease fields
                - disease_name: str
                - disease_type: str
                - description: str
                - severity_level: str
                - image: str (optional)
                - is_active: bool
        
        Returns:
            DiseaseTable: The created disease object
        """
        disease = DiseaseTable(
            disease_name=data.get("disease_name"),
            disease_type=data.get("disease_type"),
            description=data.get("description"),
            severity_level=data.get("severity_level"),
            image=data.get("image"),
            is_active=data.get("is_active", True)
        )
        
        db.session.add(disease)
        db.session.commit()
        return disease
    
    @staticmethod
    def update_disease(disease_id: int, data: dict):
        """Update an existing disease
        
        Args:
            disease_id: ID of disease to update
            data: Dictionary containing updated fields
        
        Returns:
            DiseaseTable: The updated disease object
        """
        disease = db.session.get(DiseaseTable, disease_id)
        if disease is None:
            return None
        
        disease.disease_name = data.get("disease_name", disease.disease_name)
        disease.disease_type = data.get("disease_type", disease.disease_type)
        disease.description = data.get("description", disease.description)
        disease.severity_level = data.get("severity_level", disease.severity_level)
        disease.image = data.get("image", disease.image)
        disease.is_active = data.get("is_active", disease.is_active)
        
        db.session.commit()
        return disease
    
    @staticmethod
    def delete_disease(disease_id: int):
        """Delete a disease by ID
        
        Args:
            disease_id: ID of disease to delete
        
        Returns:
            bool: True if deleted successfully, False if not found
        """
        disease = db.session.get(DiseaseTable, disease_id)
        if disease is None:
            return False
        
        db.session.delete(disease)
        db.session.commit()
        return True
    
    @staticmethod
    def get_active_diseases():
        """Get all active diseases"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.is_active == True).all()
    
    @staticmethod
    def get_diseases_by_type(disease_type: str):
        """Get all diseases of a specific type"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.disease_type == disease_type).all()
    
    @staticmethod
    def get_diseases_by_severity(severity_level: str):
        """Get all diseases of a specific severity level"""
        return db.session.query(DiseaseTable).filter(DiseaseTable.severity_level == severity_level).all()
