from extensions import db

from app.models.field_crop import FieldCropTable
from app.models.field import FieldTable
from app.models.farm import FarmTable


class FieldCropService:

    # =========================================================
    # GET ALL FIELD CROPS
    # =========================================================

    @staticmethod
    def get_all(user_id):

        try:

            crops = db.session.scalars(

                db.select(FieldCropTable)

                .join(
                    FieldCropTable.field
                )

                .join(
                    FieldTable.farm
                )

                .where(
                    FarmTable.user_id == user_id
                )

                .order_by(
                    FieldCropTable.id.desc()
                )

            ).all()

            return crops

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldCropService.get_all() error: {e}"
            )

            raise

    # =========================================================
    # GET BY ID
    # =========================================================

    @staticmethod
    def get_by_id(
        crop_id,
        user_id
    ):

        try:

            crop = db.session.scalar(

                db.select(FieldCropTable)

                .join(
                    FieldCropTable.field
                )

                .join(
                    FieldTable.farm
                )

                .where(
                    FieldCropTable.id == crop_id,
                    FarmTable.user_id == user_id
                )

            )

            return crop

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldCropService.get_by_id() error: {e}"
            )

            raise

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        field_id,
        rice_variety_id,
        growth_stage_id=None,
        planting_date=None,
        expected_harvest_date=None,
        actual_harvest_date=None,
        area=None,
        season=None,
        year=None,
        status="Active",
        description=None
    ):

        try:

            crop = FieldCropTable(

                field_id=field_id,

                rice_variety_id=rice_variety_id,

                growth_stage_id=growth_stage_id,

                planting_date=planting_date,

                expected_harvest_date=expected_harvest_date,

                actual_harvest_date=actual_harvest_date,

                area=area,
                season=season,

                year=year,

                status=status,

                description=description
            )

            db.session.add(crop)

            db.session.commit()

            db.session.refresh(crop)

            return crop

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldCropService.create() error: {e}"
            )

            raise

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update(
        crop,
        rice_variety_id,
        growth_stage_id=None,
        planting_date=None,
        expected_harvest_date=None,
        actual_harvest_date=None,
        area=None,
        season=None,
        year=None,
        status="Active",
        description=None
    ):

        try:

            crop.rice_variety_id = rice_variety_id
            crop.growth_stage_id = growth_stage_id
            crop.planting_date = planting_date
            crop.expected_harvest_date = expected_harvest_date
            crop.actual_harvest_date = actual_harvest_date
            crop.area = area
            crop.season= season,
            crop.year = year,
            crop.status = status
            crop.description = description
            db.session.commit()

            db.session.refresh(crop)

            return crop

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldCropService.update() error: {e}"
            )

            raise

    # =========================================================
    # DELETE
    # =========================================================

    @staticmethod
    def delete(crop):

        try:

            db.session.delete(crop)

            db.session.commit()

            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"FieldCropService.delete() error: {e}"
            )

            raise