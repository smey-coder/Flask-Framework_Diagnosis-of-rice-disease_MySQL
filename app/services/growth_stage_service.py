from extensions import db
from app.models.growth_stage import GrowthStageTable
from app.services.audit_service import log_audit
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

            log_audit(
                action="CREATE",
                table_name="growth_stages",
                record_id=stage.id,
                after_data={
                    "stage_name": stage_name,
                    "stage_name_kh": stage_name_kh,
                    "stage_order": stage_order,
                    "description": description,
                    "status": status
                },
                description=f"Created growth stage '{stage_name}'"
            )
            return (True,None)


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
            before_data = {
                "stage_name": growth_stage.stage_name,
                "stage_name_kh": growth_stage.stage_name_kh,
                "stage_order": growth_stage.stage_order,
                "description": growth_stage.description,
                "status": growth_stage.status
            }

            growth_stage.stage_name = stage_name
            growth_stage.stage_name_kh = stage_name_kh
            growth_stage.stage_order = stage_order
            growth_stage.description = description
            growth_stage.status = status

            db.session.commit()
            db.session.refresh(growth_stage)

            after_data = {
                "stage_name": growth_stage.stage_name,
                "stage_name_kh": growth_stage.stage_name_kh,
                "stage_order": growth_stage.stage_order,
                "description": growth_stage.description,
                "status": growth_stage.status
            }

            log_audit(
                action="UPDATE",
                table_name="growth_stages",
                record_id=growth_stage.id,
                before_data=before_data,
                after_data=after_data,
                description=f"Updated growth stage '{stage_name}'"
            )

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

            before_data = {
                "stage_name": stage.stage_name,
                "stage_name_kh": stage.stage_name_kh,
                "stage_order": stage.stage_order,
                "description": stage.description,
                "status": stage.status
            }

            # -------------------------------------------------
            # DELETE
            # -------------------------------------------------

            db.session.delete(stage)

            db.session.commit()

            log_audit(
                action="DELETE",
                table_name="growth_stages",
                record_id=stage.id,
                before_data=before_data,
                after_data=None,
                description=f"Deleted growth stage '{stage.stage_name}'"
            )

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