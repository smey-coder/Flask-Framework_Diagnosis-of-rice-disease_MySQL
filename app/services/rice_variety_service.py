from extensions import db
from app.models.rice_variety import RiceVarietyTable


class RiceVarietyService:

    # =========================================================
    # GET ALL
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

            db.session.rollback()

            print(
                f"RiceVarietyService.get_all() error: {e}"
            )

            raise

    # =========================================================
    # GET ACTIVE
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

            db.session.rollback()

            print(
                f"RiceVarietyService.get_active() error: {e}"
            )

            raise

    # =========================================================
    # GET BY ID
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

            db.session.rollback()

            print(
                f"RiceVarietyService.get_by_id() error: {e}"
            )

            raise

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        variety_name,
        name_kh,
        growth_duration_days,
        description=None,
        status="Active"
    ):

        try:

            # -------------------------------------------------
            # CHECK DUPLICATE ENGLISH NAME
            # -------------------------------------------------

            existing_name = db.session.scalar(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.variety_name
                    == variety_name
                )
            )

            if existing_name:

                return (
                    False,
                    "Rice variety name already exists."
                )

            # -------------------------------------------------
            # CHECK DUPLICATE KHMER NAME
            # -------------------------------------------------

            existing_kh = db.session.scalar(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.name_kh
                    == name_kh
                )
            )

            if existing_kh:

                return (
                    False,
                    "Khmer rice variety name already exists."
                )

            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------

            variety = RiceVarietyTable(

                variety_name=variety_name,

                name_kh=name_kh,

                growth_duration_days=
                    growth_duration_days,

                description=description,

                status=status
            )

            db.session.add(variety)

            db.session.commit()

            db.session.refresh(variety)

            return (
                True,
                None
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.create() error: {e}"
            )

            return (
                False,
                "Unable to create rice variety."
            )

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update(
        variety,
        variety_name,
        name_kh,
        growth_duration_days,
        description=None,
        status="Active"
    ):

        try:

            # -------------------------------------------------
            # CHECK DUPLICATE ENGLISH NAME
            # -------------------------------------------------

            existing_name = db.session.scalar(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.variety_name
                    == variety_name,

                    RiceVarietyTable.id
                    != variety.id
                )
            )

            if existing_name:

                return (
                    False,
                    "Rice variety name already exists."
                )

            # -------------------------------------------------
            # CHECK DUPLICATE KHMER NAME
            # -------------------------------------------------

            existing_kh = db.session.scalar(

                db.select(RiceVarietyTable)
                .where(
                    RiceVarietyTable.name_kh
                    == name_kh,

                    RiceVarietyTable.id
                    != variety.id
                )
            )

            if existing_kh:

                return (
                    False,
                    "Khmer rice variety name already exists."
                )

            # -------------------------------------------------
            # UPDATE
            # -------------------------------------------------

            variety.variety_name = variety_name

            variety.name_kh = name_kh

            variety.growth_duration_days = \
                growth_duration_days

            variety.description = description

            variety.status = status

            db.session.commit()

            db.session.refresh(variety)

            return (
                True,
                None
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.update() error: {e}"
            )

            return (
                False,
                "Unable to update rice variety."
            )

    # =========================================================
    # DELETE
    # =========================================================

    @staticmethod
    def delete(variety):

        try:

            # -------------------------------------------------
            # CHECK FIELD CROP RELATIONSHIP
            # -------------------------------------------------

            if variety.field_crops:

                return (
                    False,
                    "Cannot delete this rice variety because it is being used by a field crop."
                )

            # -------------------------------------------------
            # DELETE
            # -------------------------------------------------

            db.session.delete(variety)

            db.session.commit()

            return (
                True,
                None
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"RiceVarietyService.delete() error: {e}"
            )

            return (
                False,
                "Unable to delete rice variety."
            )