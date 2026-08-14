from extensions import db
from app.models.field import FieldTable


class FieldService:

    # =========================================================
    # GET ALL FIELDS
    # =========================================================

    @staticmethod
    def get_all(user_id):

        try:

            fields = db.session.scalars(

                db.select(FieldTable)
                .where(
                    FieldTable.farm.has(
                        user_id=user_id
                    )
                )
                .order_by(
                    FieldTable.id.desc()
                )

            ).all()

            return fields

        except Exception as e:

            print(
                f"FieldService.get_all() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # GET FIELD BY ID
    # =========================================================

    @staticmethod
    def get_by_id(field_id, user_id):

        try:

            field = db.session.scalar(

                db.select(FieldTable)
                .where(
                    FieldTable.id == field_id,
                    FieldTable.farm.has(
                        user_id=user_id
                    )
                )

            )

            return field

        except Exception as e:

            print(
                f"FieldService.get_by_id() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # CREATE FIELD
    # =========================================================

    @staticmethod
    def create(
        farm_id,
        field_name,
        area=None,
        soil_type=None,
        location=None,
        description=None,
        status="Active"
    ):

        try:

            field = FieldTable(

                farm_id=farm_id,

                field_name=field_name,

                area=area,

                soil_type=soil_type,

                location=location,

                description=description,

                status=status

            )

            db.session.add(field)

            db.session.commit()

            db.session.refresh(field)

            return field

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldService.create() error: {e}"
            )

            raise


    # =========================================================
    # UPDATE FIELD
    # =========================================================

    @staticmethod
    def update(
        field,
        field_name,
        area=None,
        soil_type=None,
        location=None,
        description=None,
        status="Active"
    ):

        try:

            field.field_name = field_name

            field.area = area

            field.soil_type = soil_type

            field.location = location

            field.description = description

            field.status = status

            db.session.commit()

            db.session.refresh(field)

            return field

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldService.update() error: {e}"
            )

            raise


    # =========================================================
    # DELETE FIELD
    # =========================================================
    @staticmethod
    def delete(field):
        try:
            db.session.delete(field)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(
                f"FieldService.delete() error: {e}"
            )
            raise