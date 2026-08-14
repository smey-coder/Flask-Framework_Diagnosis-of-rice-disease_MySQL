from sqlalchemy import func

from extensions import db

from app.models.farm import FarmTable
from app.models.field import FieldTable
from app.models.field_crop import FieldCropTable


class FarmDashboardService:

    # =====================================================
    # GET DASHBOARD STATISTICS
    # =====================================================

    @staticmethod
    def get_statistics(user_id):

        try:

            # -------------------------------------------------
            # TOTAL FARMS
            # -------------------------------------------------

            total_farms = db.session.scalar(

                db.select(
                    func.count(FarmTable.id)
                )
                .where(
                    FarmTable.user_id == user_id
                )

            ) or 0

            # -------------------------------------------------
            # ACTIVE FARMS
            # -------------------------------------------------

            active_farms = db.session.scalar(

                db.select(
                    func.count(FarmTable.id)
                )
                .where(
                    FarmTable.user_id == user_id,
                    FarmTable.status == "Active"
                )

            ) or 0

            # -------------------------------------------------
            # TOTAL FIELDS
            # -------------------------------------------------

            total_fields = db.session.scalar(

                db.select(
                    func.count(FieldTable.id)
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id
                )

            ) or 0

            # -------------------------------------------------
            # ACTIVE FIELDS
            # -------------------------------------------------

            active_fields = db.session.scalar(

                db.select(
                    func.count(FieldTable.id)
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id,
                    FieldTable.status == "Active"
                )

            ) or 0

            # -------------------------------------------------
            # TOTAL AREA
            # -------------------------------------------------

            total_area = db.session.scalar(

                db.select(
                    func.coalesce(
                        func.sum(FieldTable.area),
                        0
                    )
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id
                )

            ) or 0

            # -------------------------------------------------
            # TOTAL FIELD CROPS
            # -------------------------------------------------

            total_crops = db.session.scalar(

                db.select(
                    func.count(FieldCropTable.id)
                )
                .join(
                    FieldCropTable.field
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id
                )

            ) or 0

            # -------------------------------------------------
            # ACTIVE CROPS
            # -------------------------------------------------

            active_crops = db.session.scalar(

                db.select(
                    func.count(FieldCropTable.id)
                )
                .join(
                    FieldCropTable.field
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id,
                    FieldCropTable.status == "Active"
                )

            ) or 0

            # -------------------------------------------------
            # HARVESTED CROPS
            # -------------------------------------------------

            harvested_crops = db.session.scalar(

                db.select(
                    func.count(FieldCropTable.id)
                )
                .join(
                    FieldCropTable.field
                )
                .join(
                    FieldTable.farm
                )
                .where(
                    FarmTable.user_id == user_id,
                    FieldCropTable.status == "Harvested"
                )

            ) or 0

            # -------------------------------------------------
            # RETURN
            # -------------------------------------------------

            return {
                "total_farms": total_farms,
                "active_farms": active_farms,

                "total_fields": total_fields,
                "active_fields": active_fields,

                "total_area": float(total_area),

                "total_crops": total_crops,
                "active_crops": active_crops,
                "harvested_crops": harvested_crops
            }

        except Exception as e:

            db.session.rollback()

            print(
                f"FarmDashboardService.get_statistics() error: {e}"
            )

            raise