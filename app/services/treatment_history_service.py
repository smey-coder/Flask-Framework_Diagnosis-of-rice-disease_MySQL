
from sqlalchemy import or_

from extensions import db

from app.models.treatments import TreatmentTable
from app.models.treatment_histories import TreatmentHistoryTable


class TreatmentHistoryService:

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        monitoring_id,
        diagnosis_history_id,
        treatment_id,
        treatment_date,
        status="planned",
        result=None,
        notes=None
    ):

        try:

            treatment_history = TreatmentHistoryTable(
                monitoring_id=monitoring_id,
                diagnosis_history_id=diagnosis_history_id,
                treatment_id=treatment_id,
                treatment_date=treatment_date,
                status=status,
                result=result,
                notes=notes
            )

            db.session.add(treatment_history)
            db.session.commit()

            return treatment_history

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Create Error: {e}"
            )

            return None


    # =====================================================
    # GET BY ID
    # =====================================================

    @staticmethod
    def get_by_id(history_id):

        try:

            return (
                TreatmentHistoryTable.query
                .filter(
                    TreatmentHistoryTable.id == history_id
                )
                .first()
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Get Error: {e}"
            )

            return None


    # =====================================================
    # GET BY MONITORING
    # =====================================================

    @staticmethod
    def get_by_monitoring(monitoring_id):

        try:

            return (
                TreatmentHistoryTable.query
                .filter(
                    TreatmentHistoryTable.monitoring_id
                    == monitoring_id
                )
                .order_by(
                    TreatmentHistoryTable.treatment_date.desc()
                )
                .all()
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Monitoring Error: {e}"
            )

            return []


    # =====================================================
    # GET BY DIAGNOSIS
    # =====================================================

    @staticmethod
    def get_by_diagnosis(diagnosis_history_id):

        try:

            return (
                TreatmentHistoryTable.query
                .filter(
                    TreatmentHistoryTable.diagnosis_history_id
                    == diagnosis_history_id
                )
                .order_by(
                    TreatmentHistoryTable.treatment_date.desc()
                )
                .all()
            )

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Diagnosis Error: {e}"
            )

            return []


    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        history,
        treatment_date=None,
        status=None,
        result=None,
        notes=None
    ):

        try:

            if treatment_date is not None:

                history.treatment_date = treatment_date


            if status is not None:

                history.status = status


            if result is not None:

                history.result = result


            if notes is not None:

                history.notes = notes


            db.session.commit()

            return history

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Update Error: {e}"
            )

            return None


    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(history):

        try:

            db.session.delete(history)

            db.session.commit()

            return True

        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Delete Error: {e}"
            )

            return False


    # =====================================================
    # PAGINATION
    # =====================================================

    @staticmethod
    def paginate(
        page=1,
        per_page=10,
        monitoring_id=None,
        diagnosis_history_id=None,
        status=None,
        search=None
    ):

        try:

            # =================================================
            # BASE QUERY
            # =================================================

            query = (
                TreatmentHistoryTable.query
                .outerjoin(
                    TreatmentTable,
                    TreatmentHistoryTable.treatment_id
                    == TreatmentTable.id
                )
            )


            # =================================================
            # MONITORING FILTER
            # =================================================

            if monitoring_id is not None:

                query = query.filter(
                    TreatmentHistoryTable.monitoring_id
                    == monitoring_id
                )


            # =================================================
            # DIAGNOSIS FILTER
            # =================================================

            if diagnosis_history_id is not None:

                query = query.filter(
                    TreatmentHistoryTable.diagnosis_history_id
                    == diagnosis_history_id
                )


            # =================================================
            # STATUS FILTER
            # =================================================

            if status:

                query = query.filter(
                    TreatmentHistoryTable.status
                    == status
                )


            # =================================================
            # SEARCH
            # =================================================

            if search:

                keyword = f"%{search.strip()}%"

                query = query.filter(
                    or_(
                        TreatmentHistoryTable.result.ilike(
                            keyword
                        ),

                        TreatmentHistoryTable.notes.ilike(
                            keyword
                        ),

                        TreatmentTable.method.ilike(
                            keyword
                        ),

                        TreatmentTable.treatment_type.ilike(
                            keyword
                        )
                    )
                )


            # =================================================
            # ORDER
            # =================================================

            query = query.order_by(
                TreatmentHistoryTable.treatment_date.desc()
            )


            # =================================================
            # PAGINATION
            # =================================================

            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return pagination


        except Exception as e:

            db.session.rollback()

            print(
                f"Treatment History Pagination Error: {e}"
            )

            return None

