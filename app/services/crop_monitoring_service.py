from flask_login import current_user

from app.models.UserNotification import UserNotification
from app.models.field import FieldTable
from app.models.field_crop import FieldCropTable
from app.models.growth_stage import GrowthStageTable
from extensions import db

from app.models.crop_monitoring import CropMonitoringTable
from app.services.audit_service import log_audit


class CropMonitoringService:

    @staticmethod
    def _sync_field_crop_harvest_stage(field_crop_id, growth_stage_id):
        if not growth_stage_id:
            return None

        growth_stage = db.session.get(GrowthStageTable, growth_stage_id)
        if (
            not growth_stage
            or (growth_stage.stage_name or "").strip().casefold() != "harvest"
        ):
            return None

        field_crop = db.session.get(FieldCropTable, field_crop_id)
        if not field_crop or field_crop.growth_stage_id == growth_stage.id:
            return None

        previous_stage_id = field_crop.growth_stage_id
        field_crop.growth_stage_id = growth_stage.id
        return field_crop, previous_stage_id

    @staticmethod
    def _log_field_crop_stage_sync(stage_sync):
        if not stage_sync:
            return

        field_crop, previous_stage_id = stage_sync
        log_audit(
            action="UPDATE",
            table_name="field_crops",
            record_id=field_crop.id,
            before_data={"growth_stage_id": previous_stage_id},
            after_data={"growth_stage_id": field_crop.growth_stage_id},
            description="Synchronized growth stage from harvest monitoring"
        )

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

            # =====================================================
            # CREATE CROP MONITORING
            # =====================================================

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

            db.session.add(monitoring)

            field_crop_stage_sync = (
                CropMonitoringService._sync_field_crop_harvest_stage(
                    field_crop_id,
                    growth_stage_id
                )
            )

            # =====================================================
            # GET AUTO-INCREMENT monitoring.id
            # =====================================================

            db.session.flush()

            print(
                "Created monitoring ID:",
                monitoring.id
            )

            # =====================================================
            # CREATE NOTIFICATION
            # =====================================================

            notification = UserNotification(
                user_id=current_user.id,
                # Crop monitoring notification
                disease_id=None,
                # Now monitoring.id exists
                monitoring_id=monitoring.id,
                category="crop_monitoring",
                is_read=False,
                is_deleted=False
            )

            db.session.add(notification)

            # =====================================================
            # SAVE BOTH
            # =====================================================

            db.session.commit()
            CropMonitoringService._log_field_crop_stage_sync(
                field_crop_stage_sync
            )

            # =====================================================
            # REFRESH MONITORING
            # =====================================================

            db.session.refresh(monitoring)

            print(
                "Notification created:",
                notification.id,
                "Monitoring:",
                notification.monitoring_id
            )

            log_audit(
                action="CREATE",
                table_name="crop_monitoring",
                record_id=monitoring.id,
                after_data={
                    "field_crop_id": monitoring.field_crop_id,
                    "monitoring_date": str(monitoring.monitoring_date),
                    "growth_stage_id": monitoring.growth_stage_id,
                    "plant_height": monitoring.plant_height,
                    "water_status": monitoring.water_status,
                    "plant_condition": monitoring.plant_condition,
                    "pest_status": monitoring.pest_status,
                    "disease_status": monitoring.disease_status,
                    "description": monitoring.description
                }
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
            field_crop_id = monitoring.field_crop_id

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

            field_crop_stage_sync = (
                CropMonitoringService._sync_field_crop_harvest_stage(
                    field_crop_id,
                    growth_stage_id
                )
            )

            db.session.commit()
            CropMonitoringService._log_field_crop_stage_sync(
                field_crop_stage_sync
            )

            db.session.refresh(
                monitoring
            )

            log_audit(
                action="UPDATE",
                table_name="crop_monitoring",
                record_id=monitoring.id,
                after_data={
                    "field_crop_id": monitoring.field_crop_id,
                    "monitoring_date": str(monitoring.monitoring_date),
                    "growth_stage_id": monitoring.growth_stage_id,
                    "plant_height": monitoring.plant_height,
                    "water_status": monitoring.water_status,
                    "plant_condition": monitoring.plant_condition,
                    "pest_status": monitoring.pest_status,
                    "disease_status": monitoring.disease_status,
                    "description": monitoring.description
                }
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

            log_audit(
                action="DELETE",
                table_name="crop_monitoring",
                record_id=monitoring.id,
                before_data={
                    "field_crop_id": monitoring.field_crop_id,
                    "monitoring_date": str(monitoring.monitoring_date),
                    "growth_stage_id": monitoring.growth_stage_id,
                    "plant_height": monitoring.plant_height,
                    "water_status": monitoring.water_status,
                    "plant_condition": monitoring.plant_condition,
                    "pest_status": monitoring.pest_status,
                    "disease_status": monitoring.disease_status,
                    "description": monitoring.description
                }
            )
            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.delete() error: {e}"
            )

            raise
    @staticmethod
    def get_latest_by_field_crop(user_id):
        try:
            # Get all monitoring records
            monitorings = CropMonitoringTable.query \
                .join(
                    FieldCropTable,
                    CropMonitoringTable.field_crop_id == FieldCropTable.id
                ) \
                .join(
                    FieldTable,
                    FieldCropTable.field_id == FieldTable.id
                ) \
                .filter(
                    FieldTable.farm.has(user_id=user_id)
                ) \
                .order_by(
                    CropMonitoringTable.field_crop_id.asc(),
                    CropMonitoringTable.monitoring_date.desc(),
                    CropMonitoringTable.id.desc()
                ).all()

            latest = {}

            for monitoring in monitorings:

                crop_id = monitoring.field_crop_id

                if crop_id not in latest:
                    latest[crop_id] = monitoring

            return list(latest.values())

        except Exception as e:

            db.session.rollback()

            print(
                f"CropMonitoringService.get_latest_by_field_crop() error: {e}"
            )

            raise