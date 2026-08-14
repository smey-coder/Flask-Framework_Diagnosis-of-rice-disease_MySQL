from extensions import db

from app.models.crop_monitoring import CropMonitoringTable
from app.models.field_crop import FieldCropTable


class CropMonitoringService:

    # =========================================================
    # GET ALL MONITORINGS
    # =========================================================

    @staticmethod
    def get_all(user_id):

        try:

            monitorings = db.session.scalars(

                db.select(
                    CropMonitoringTable
                )
                .join(
                    CropMonitoringTable.field_crop
                )
                .where(
                    FieldCropTable.field.has(
                        FieldCropTable.field.property.mapper.class_.farm.has(
                            user_id=user_id
                        )
                    )
                )
                .order_by(
                    CropMonitoringTable.monitoring_date.desc(),
                    CropMonitoringTable.id.desc()
                )

            ).all()

            return monitorings

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.get_all() error: {e}"
            )

            raise

    # =========================================================
    # GET BY ID
    # =========================================================

    @staticmethod
    def get_by_id(
        monitoring_id,
        user_id
    ):

        try:

            monitoring = db.session.scalar(

                db.select(
                    CropMonitoringTable
                )
                .join(
                    CropMonitoringTable.field_crop
                )
                .where(
                    CropMonitoringTable.id == monitoring_id,

                    FieldCropTable.field.has(
                        FieldCropTable.field.property.mapper.class_.farm.has(
                            user_id=user_id
                        )
                    )
                )

            )

            return monitoring

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.get_by_id() error: {e}"
            )

            raise

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        field_crop_id,
        monitoring_date,
        growth_stage_id=None,
        plant_height=None,
        water_status=None,
        plant_condition=None,
        pest_status=None,
        disease_status=None,
        description=None
    ):

        try:

            monitoring = CropMonitoringTable(

                field_crop_id=field_crop_id,

                monitoring_date=monitoring_date,

                growth_stage_id=growth_stage_id,

                plant_height=plant_height,

                water_status=water_status,

                plant_condition=plant_condition,

                pest_status=pest_status,

                disease_status=disease_status,

                description=description
            )

            db.session.add(
                monitoring
            )

            db.session.commit()

            db.session.refresh(
                monitoring
            )

            return monitoring

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.create() error: {e}"
            )

            raise

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update(
        monitoring,
        monitoring_date,
        growth_stage_id=None,
        plant_height=None,
        water_status=None,
        plant_condition=None,
        pest_status=None,
        disease_status=None,
        description=None
    ):

        try:

            monitoring.monitoring_date = (
                monitoring_date
            )

            monitoring.growth_stage_id = (
                growth_stage_id
            )

            monitoring.plant_height = (
                plant_height
            )

            monitoring.water_status = (
                water_status
            )

            monitoring.plant_condition = (
                plant_condition
            )

            monitoring.pest_status = (
                pest_status
            )

            monitoring.disease_status = (
                disease_status
            )

            monitoring.description = (
                description
            )

            db.session.commit()

            db.session.refresh(
                monitoring
            )

            return monitoring

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.update() error: {e}"
            )

            raise

    # =========================================================
    # DELETE
    # =========================================================

    @staticmethod
    def delete(monitoring):

        try:

            db.session.delete(
                monitoring
            )

            db.session.commit()

            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.delete() error: {e}"
            )

            raise