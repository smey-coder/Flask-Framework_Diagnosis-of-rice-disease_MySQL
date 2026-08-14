from extensions import db
from app.models.rice_variety import RiceVarietyTable


class RiceVarietyService:

    # =========================================================
    # GET ALL RICE VARIETIES
    # =========================================================

    @staticmethod
    def get_all():

        try:

            varieties = db.session.scalars(

                db.select(RiceVarietyTable)
                .order_by(
                    RiceVarietyTable.id.desc()
                )

            ).all()

            return varieties

        except Exception as e:

            print(
                f"RiceVarietyService.get_all() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # GET ACTIVE RICE VARIETIES
    # =========================================================

    @staticmethod
    def get_active():
        try:
            varieties = db.session.scalars(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.status == "Active"
                )
                .order_by(
                    RiceVarietyTable.name_kh.asc()
                )

            ).all()

            return varieties

        except Exception as e:

            print(
                f"RiceVarietyService.get_active() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # GET RICE VARIETY BY ID
    # =========================================================

    @staticmethod
    def get_by_id(variety_id):

        try:

            variety = db.session.scalar(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.id == variety_id
                )

            )

            return variety

        except Exception as e:

            print(
                f"RiceVarietyService.get_by_id() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # CREATE RICE VARIETY
    # =========================================================

    @staticmethod
    def create(
        name,
        description=None,
        status="Active"
    ):

        try:
            variety = RiceVarietyTable(
                name=name,
                description=description,
                status=status
            )

            db.session.add(variety)

            db.session.commit()

            db.session.refresh(variety)

            return variety

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.create() error: {e}"
            )

            raise


    # =========================================================
    # UPDATE RICE VARIETY
    # =========================================================

    @staticmethod
    def update(
        variety,
        name,
        description=None,
        status="Active"
    ):

        try:

            variety.name = name

            variety.description = description

            variety.status = status

            db.session.commit()

            db.session.refresh(variety)

            return variety

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.update() error: {e}"
            )

            raise


    # =========================================================
    # DELETE RICE VARIETY
    # =========================================================

    @staticmethod
    def delete(variety):

        try:

            db.session.delete(variety)

            db.session.commit()

            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.delete() error: {e}"
            )

            raise