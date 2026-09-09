from extensions import db
from app.models.farm import FarmTable
from app.services.audit_service import log_audit
class FarmService:

    @staticmethod
    def get_all(user_id=None):
        query = FarmTable.query
        if user_id is not None:
            query = query.filter(
                FarmTable.user_id == user_id
            )
        return query.order_by(
            FarmTable.created_at.desc()
        ).all()

    @staticmethod
    def get_by_id(farm_id, user_id=None):
        query = FarmTable.query.filter(
            FarmTable.id == farm_id
        )
        if user_id is not None:
            query = query.filter(
                FarmTable.user_id == user_id
            )
        return query.first()

    @staticmethod
    def create(
        user_id,
        farm_name,
        province,
        district,
        commune,
        description=None,
        location=None,
        status="Active"
       
    ):
        farm = FarmTable(
            user_id=user_id,
            farm_name=farm_name,
            province=province,
            district=district,
            commune=commune,
            description=description,
            location=location,
            status=status
        )
        db.session.add(farm)
        db.session.commit()
        log_audit(
            action="CREATE",
            table_name="farms",
            record_id=farm.id,
            after_data={
                "user_id": user_id,
                "farm_name": farm_name,
                "province": province,
                "district": district,
                "commune": commune,
                "description": description,
                "location": location,
                "status": status
            }
        )
        return farm
    @staticmethod
    def update(
        farm,
        farm_name,
        province,
        district,
        commune,
        description=None,
        location=None,
        status=None
    ):
        farm.farm_name = farm_name
        farm.province = province
        farm.district = district
        farm.commune = commune
        farm.description = description
        farm.location = location
    
        if status is not None:
            farm.status = status
        db.session.commit()

        log_audit(
            action="UPDATE",
            table_name="farms",
            record_id=farm.id,
            after_data={
                "farm_name": farm_name,
                "province": province,
                "district": district,
                "commune": commune,
                "description": description,
                "location": location,
                "status": status
            }
        )
        return farm
    
    @staticmethod
    def delete(farm):
        db.session.delete(farm)
        db.session.commit()

        log_audit(
            action="DELETE",
            table_name="farms",
            record_id=farm.id,
            before_data={
                "user_id": farm.user_id,
                "farm_name": farm.farm_name,
                "province": farm.province,
                "district": farm.district,
                "commune": farm.commune,
                "description": farm.description,
                "location": farm.location,
                "status": farm.status
            }
        )
        return True