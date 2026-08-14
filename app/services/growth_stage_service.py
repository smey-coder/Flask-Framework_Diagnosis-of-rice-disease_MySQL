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
                    GrowthStageTable.stage_name.asc()
                )

            ).all()
            return stages
        except Exception as e:
            print(f"GrowthStageService.get_all() error: {e}")
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

            print("Growth stages:", stages)
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
        stage_order,
        description=None,
        status="Active"
    ):

        try:

            stage = GrowthStageTable(

                stage_name=stage_name,

                stage_order=stage_order,

                description=description,

                status=status

            )

            db.session.add(stage)

            db.session.commit()

            db.session.refresh(stage)

            return stage

        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.create() error: {e}"
            )

            raise


    # =========================================================
    # UPDATE GROWTH STAGE
    # =========================================================

    @staticmethod
    def update(
        stage,
        stage_name,
        stage_order,
        description=None,
        status="Active"
    ):

        try:

            stage.stage_name = stage_name

            stage.stage_order = stage_order

            stage.description = description

            stage.status = status

            db.session.commit()

            db.session.refresh(stage)

            return stage

        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.update() error: {e}"
            )

            raise


    # =========================================================
    # DELETE GROWTH STAGE
    # =========================================================

    @staticmethod
    def delete(stage):

        try:

            db.session.delete(stage)

            db.session.commit()

            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"GrowthStageService.delete() error: {e}"
            )

            raise