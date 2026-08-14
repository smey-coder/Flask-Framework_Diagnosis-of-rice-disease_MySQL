from extensions import db
from app.models.farm import FarmTable
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
        description=None,
        location=None,
        status="Active"
       
    ):
        farm = FarmTable(
            user_id=user_id,
            farm_name=farm_name,
            description=description,
            location=location,
            status=status
        )
        db.session.add(farm)
        db.session.commit()
        return farm
    @staticmethod
    def update(
        farm,
        farm_name,
        description=None,
        location=None,
        status=None
    ):
        farm.farm_name = farm_name
        farm.description = description
        farm.location = location
    
        if status is not None:
            farm.status = status
        db.session.commit()
        return farm
    
    @staticmethod
    def delete(farm):
        db.session.delete(farm)
        db.session.commit()

        return True