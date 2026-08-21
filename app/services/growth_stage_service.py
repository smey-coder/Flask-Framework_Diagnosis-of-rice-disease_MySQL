from extensions import db
from app.models.growth_stage import GrowthStageTable


class GrowthStageService:

    # =========================================================
    # GET ALL GROWTH STAGES
    # =========================================================

    @staticmethod
    def get_all():

        try:

            stages = db.session.scalars(
                db.select(GrowthStageTable)
                .order_by(
                    GrowthStageTable.stage_order.asc()
                )
            ).all()

            return stages

        except Exception as e:

            print(
                f"GrowthStageService.get_all() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # GET ACTIVE GROWTH STAGES
    # =========================================================

    @staticmethod
    def get_active():

        try:

            stages = db.session.scalars(
                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.status == "Active"
                )
                .order_by(
                    GrowthStageTable.stage_order.asc()
                )
            ).all()

            return stages

        except Exception as e:

            print(
                f"GrowthStageService.get_active() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # GET GROWTH STAGE BY ID
    # =========================================================

    @staticmethod
    def get_by_id(stage_id):

        try:

            stage = db.session.scalar(

                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.id == stage_id
                )

            )

            return stage

        except Exception as e:

            print(
                f"GrowthStageService.get_by_id() error: {e}"
            )

            db.session.rollback()

            raise


    # =========================================================
    # CREATE GROWTH STAGE
    # =========================================================

    @staticmethod
    def create(
        stage_name,
        stage_name_kh,
        stage_order,
        description=None,
        status="Active"
    ):

        try:

            # -------------------------------------------------
            # CHECK DUPLICATE STAGE NAME
            # -------------------------------------------------

            existing_name = db.session.scalar(

                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.stage_name == stage_name
                )

            )

            if existing_name:

                return (
                    False,
                    "Growth stage name already exists."
                )


            # -------------------------------------------------
            # CHECK DUPLICATE STAGE ORDER
            # -------------------------------------------------

            existing_order = db.session.scalar(

                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.stage_order == stage_order
                )

            )

            if existing_order:

                return (
                    False,
                    "Growth stage order already exists."
                )


            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------

            stage = GrowthStageTable(

                stage_name=stage_name,

                stage_name_kh=stage_name_kh,

                stage_order=stage_order,

                description=description,

                status=status
            )

            db.session.add(stage)

            db.session.commit()

            db.session.refresh(stage)


            return (
                True,
                None
            )


        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.create() error: {e}"
            )

            return (
                False,
                "Unable to create growth stage."
            )


    # =========================================================
    # UPDATE GROWTH STAGE
    # =========================================================

    @staticmethod
    def update(
        growth_stage,
        stage_name,
        stage_name_kh,
        stage_order,
        description=None,
        status="Active"
    ):

        try:

            # -------------------------------------------------
            # CHECK DUPLICATE STAGE NAME
            # -------------------------------------------------

            existing_name = db.session.scalar(

                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.stage_name == stage_name,
                    GrowthStageTable.id != growth_stage.id
                )

            )

            if existing_name:
                return (
                    False,
                    "Growth stage name already exists."
                )


            # -------------------------------------------------
            # CHECK DUPLICATE STAGE ORDER
            # -------------------------------------------------

            existing_order = db.session.scalar(

                db.select(GrowthStageTable)
                .where(
                    GrowthStageTable.stage_order == stage_order,
                    GrowthStageTable.id != growth_stage.id
                )

            )

            if existing_order:
                return (
                    False,
                    "Growth stage order already exists."
                )


            # -------------------------------------------------
            # UPDATE
            # -------------------------------------------------

            growth_stage.stage_name = stage_name

            growth_stage.stage_name_kh = stage_name_kh

            growth_stage.stage_order = stage_order

            growth_stage.description = description

            growth_stage.status = status


            db.session.commit()

            db.session.refresh(growth_stage)


            return (
                True,
                None
            )


        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.update() error: {e}"
            )

            return (
                False,
                "Unable to update growth stage."
            )


    # =========================================================
    # DELETE GROWTH STAGE
    # =========================================================

    @staticmethod
    def delete(stage):
        try:
            # -------------------------------------------------
            # CHECK FIELD CROP RELATIONSHIP
            # -------------------------------------------------

            if stage.field_crops:

                return (
                    False,
                    "Cannot delete this growth stage because it is being used by a field crop."
                )


            # -------------------------------------------------
            # CHECK MONITORING RELATIONSHIP
            # -------------------------------------------------

            if stage.monitorings:

                return (
                    False,
                    "Cannot delete this growth stage because it is being used by crop monitoring."
                )


            # -------------------------------------------------
            # DELETE
            # -------------------------------------------------

            db.session.delete(stage)

            db.session.commit()


            return (
                True,
                None
            )


        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.delete() error: {e}"
            )

            return (
                False,
                "Unable to delete growth stage."
            )