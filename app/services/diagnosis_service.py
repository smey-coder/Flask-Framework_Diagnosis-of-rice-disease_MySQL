from typing import Dict, List, Set, Tuple
from app.models.rules import RulesTable
from app.models.diseases import DiseaseTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.symptoms import SymptomsTable
from app.models.treatments import TreatmentTable
from app.models.preventions import PreventionTable
from app.services.audit_service import log_audit

class DiagnosisService:
    """
    Expert system service using MYCIN certainty factor.
    Supports partial matches and explanation logs.
    """
    @staticmethod
    def combine_cfs(cf1: float, cf2: float) -> float:
        """Combine two certainty factors using MYCIN formula."""
        return cf1 + cf2 * (1 - cf1)
    
    @classmethod
    def infer(cls, selected_symptom_ids: List[int]) -> Tuple[Dict[int, dict], Dict[str, List[dict]], List[dict]]:
        """
        Infer diseases based on selected symptoms.
        Returns:
            conclusions: {disease_id: {"disease": DiseaseTable, "certainty": float}}
            rule_trace: applied rules per disease
            skipped_rules: rules not satisfied
        """
        facts: Set[int] = set(selected_symptom_ids or [])
        conclusions: Dict[int, dict] = {}
        rule_trace: Dict[str, List[dict]] = {}
        skipped_rules: List[dict] = []

        # Prefetch all active rules, diseases, and symptoms
        rules = RulesTable.query.filter_by(is_active=True).all() or []
        diseases = {d.id: d for d in DiseaseTable.query.all()}
        symptoms = {s.id: s for s in SymptomsTable.query.all()}

        for rule in rules:
            disease = diseases.get(rule.disease_id)
            if not disease:
                continue

            conditions = RuleConditionsTable.query.filter_by(rule_id=rule.id, is_active=True).all() or []
            condition_ids = {c.symptom_id for c in conditions}
            if not condition_ids:
                continue
            matched_ids = condition_ids & facts
            matched_count = len(matched_ids)
            total_count = len(condition_ids)

            if matched_count > 0:
                # Partial CF based on matched symptoms
                rule_cf = float(getattr(rule, "certainty", 0))
                adjusted_cf = rule_cf * (matched_count / total_count)

                # Initialize disease in conclusions if not present
                if disease.id not in conclusions:
                    conclusions[disease.id] = {"disease": disease, "certainty": 0.0}
                    rule_trace[str(disease.id)] = []

                # Get CF before applying this rule
                prev_cf = conclusions[disease.id]["certainty"]

                # Combine previous CF with this rule
                new_cf = cls.combine_cfs(prev_cf, adjusted_cf)
                conclusions[disease.id]["certainty"] = new_cf

                matched_names = [symptoms[sid].symptom_name for sid in matched_ids if sid in symptoms]

                rule_trace[str(disease.id)].append({
                    "rule_id": rule.id,
                    "matched": matched_names,
                    "cf_before": round(prev_cf, 3),   # previous CF before applying rule
                    "rule_cf": round(adjusted_cf, 3), # this rule's CF contribution
                    "cf_after": round(new_cf, 3),     # cumulative CF after applying rule
                    "explanation": getattr(rule, "explanation", "")
                })
            else:
                # Track skipped rules
                missing_names = [symptoms[sid].symptom_name for sid in condition_ids if sid in symptoms]
                skipped_rules.append({
                    "rule_id": rule.id,
                    "disease": disease.disease_name,
                    "missing": missing_names
                })

        # Sort conclusions by certainty descending
        sorted_conclusions = dict(
            sorted(conclusions.items(), key=lambda item: item[1]['certainty'], reverse=True)
        )

        # ==========================
        # Audit Log
        # ==========================
        try:
            diagnosis_results = []
            for disease_id, result in sorted_conclusions.items():
                diagnosis_results.append({
                    "disease_id": disease_id,
                    "disease_name": result["disease"].disease_name,
                    "certainty": round(result["certainty"] * 100, 2)
                })
            log_audit(
                action="Diagnosis",
                table_name="diagnosis_history",
                record_id=0,
                before_data=None,
                after_data={
                    "description": "User diagnosed rice disease.",
                    "selected_symptoms": selected_symptom_ids,
                    "diagnosis_results": diagnosis_results
                }
            )
        except Exception as e:
            print(f"Audit Error: {e}")
        return sorted_conclusions, rule_trace, skipped_rules
    
    @staticmethod
    def explain_disease(disease_id: int, rule_trace: Dict[str, List[dict]]) -> List[dict]:
        # Make sure ID is string (keys in rule_trace are strings)
        disease_id = str(disease_id)

        return rule_trace.get(disease_id, [])

    # ---- Backward compatible: allow optional rule_trace argument ----
    @staticmethod
    def treatment_disease(disease_id: int, rule_trace=None) -> List[dict]:
        """
        Get active treatments for a disease.
        Treatments are ordered by priority.
        Lower priority number = higher recommendation.
        Example:
            priority 1 = Best recommendation
            priority 2 = Alternative
            priority 3 = Other option
        """
        treatments = (
            TreatmentTable.query
            .filter(
                TreatmentTable.disease_id == disease_id,
                TreatmentTable.is_active == True
            )
            .order_by(
                TreatmentTable.priority.asc(),
                TreatmentTable.id.asc()
            )
            .all()
        )

        return [
            {
                "id": t.id,
                "treatment_type": t.treatment_type,
                "method": t.method,
                "description": t.description,
                "image": t.image,
                "priority": t.priority
            }
            for t in treatments
        ]
    @staticmethod
    def prevention_disease(disease_id: int, rule_trace=None) -> List[dict]:
        """
        Get active prevention methods for a disease.
        """

        preventions = (
            PreventionTable.query
            .filter(
                PreventionTable.disease_id == disease_id,
                PreventionTable.is_active == True
            )
            .order_by(
                PreventionTable.priority.asc(),
                PreventionTable.id.asc()
            )
            .all()
        )

        return [
            {
                "id": p.id,
                "prevention_type": p.prevention_type,
                "method": p.method,
                "description": p.description,
                "priority": p.priority,
                "image": p.image
            }
            for p in preventions
        ]
    @staticmethod
    def recommend_prevention(disease_id: int) -> dict | None:

        prevention = (
            PreventionTable.query
            .filter(
                PreventionTable.disease_id == disease_id,
                PreventionTable.is_active == True
            )
            .order_by(
                PreventionTable.priority.asc(),
                PreventionTable.id.asc()
            )
            .first()
        )

        if not prevention:
            return None

        return {
            "id": prevention.id,
            "prevention_type": prevention.prevention_type,
            "method": prevention.method,
            "description": prevention.description,
            "image": prevention.image,
            "priority": prevention.priority
        }

    @staticmethod
    def recommend_treatment(disease_id: int) -> dict | None:
        """
        Return the highest-priority treatment for a disease.
        """

        treatment = (
            TreatmentTable.query
            .filter(
                TreatmentTable.disease_id == disease_id,
                TreatmentTable.is_active == True
            )
            .order_by(
                TreatmentTable.priority.asc(),
                TreatmentTable.id.asc()
            )
            .first()
        )

        if not treatment:
            return None

        return {
            "id": treatment.id,
            "treatment_type": treatment.treatment_type,
            "method": treatment.method,
            "description": treatment.description,
            "image": treatment.image,
            "priority": treatment.priority
        }
    @staticmethod
    def get_treatment_recommendation(
        disease_id: int,
        certainty: float
    ) -> dict:

        # =====================================================
        # GET BEST TREATMENT
        # =====================================================

        treatment = DiagnosisService.recommend_treatment(
            disease_id
        )

        # =====================================================
        # NO TREATMENT AVAILABLE
        # =====================================================

        if not treatment:

            return {
                "status": "no_treatment",
                "level": "none",
                "message": (
                    "No treatment recommendation is "
                    "available for this disease."
                ),
                "treatment": None,
                "warning": None
            }

        # =====================================================
        # HIGH CERTAINTY
        # =====================================================

        if certainty >= 0.70:

            return {
                "status": "recommended",
                "level": "high",
                "message": (
                    "This treatment is recommended "
                    "based on the diagnosis."
                ),
                "treatment": treatment,
                "warning": None
            }

        # =====================================================
        # MEDIUM CERTAINTY
        # =====================================================

        elif certainty >= 0.40:

            return {
                "status": "verify",
                "level": "medium",
                "message": (
                    "This treatment may be suitable, "
                    "but the diagnosis should be verified."
                ),
                "treatment": treatment,
                "warning": (
                    "Diagnosis confidence is moderate. "
                    "Please verify the symptoms before "
                    "applying treatment."
                )
            }

        # =====================================================
        # LOW CERTAINTY
        # =====================================================

        else:

            return {
                "status": "insufficient",
                "level": "low",
                "message": (
                    "The diagnosis confidence is too low "
                    "to strongly recommend treatment."
                ),
                "treatment": None,
                "warning": (
                    "Please select additional symptoms "
                    "or verify the diagnosis."
                )
            }