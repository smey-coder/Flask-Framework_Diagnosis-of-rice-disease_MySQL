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
            rule_trace: applied rules per disease (keyed by str disease_id)
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

            str_disease_id = str(disease.id)

            if matched_count > 0:
                # Get certainty directly from tbl_rule / RulesTable
                rule_cf = float(getattr(rule, "certainty", 0.0) or 0.0)
                adjusted_cf = rule_cf * (matched_count / total_count)

                # 1. Initialize disease entry in conclusions
                if disease.id not in conclusions:
                    conclusions[disease.id] = {"disease": disease, "certainty": 0.0}
                
                # 2. Guarantee rule_trace key exists for string ID
                if str_disease_id not in rule_trace:
                    rule_trace[str_disease_id] = []

                # 3. Read current certainty BEFORE applying this rule
                prev_cf = float(conclusions[disease.id]["certainty"])

                # 4. Combine previous CF with this rule's contribution
                new_cf = cls.combine_cfs(prev_cf, adjusted_cf)
                conclusions[disease.id]["certainty"] = new_cf

                matched_names = [symptoms[sid].symptom_name for sid in matched_ids if sid in symptoms]

                # 5. Append step trace with accurate prev_cf
                rule_trace[str_disease_id].append({
                    "rule_id": rule.id,
                    "matched": matched_names,
                    "cf_before": float(round(prev_cf, 4)),       # CF prior to applying this rule
                    "rule_cf": float(round(adjusted_cf, 4)),     # Adjusted CF contribution from tbl_rule
                    "cf_after": float(round(new_cf, 4)),          # Combined CF after rule application
                    "explanation": getattr(rule, "explanation", "") or ""
                })
            else:
                # Track skipped rules
                missing_names = [symptoms[sid].symptom_name for sid in condition_ids if sid in symptoms]
                current_disease_cf = conclusions.get(disease.id, {}).get("certainty", 0.0)
                
                skipped_rules.append({
                    "rule_id": rule.id,
                    "disease": disease.disease_name,
                    "missing": missing_names,
                    "cf_before": float(round(current_disease_cf, 4)),
                    "rule_cf": 0.0,
                    "cf_after": float(round(current_disease_cf, 4)),
                    "explanation": "No symptoms matched for this rule."
                })

        # Sort conclusions by certainty descending
        sorted_conclusions = dict(
            sorted(conclusions.items(), key=lambda item: item[1]['certainty'], reverse=True)
        )

        # Audit Log execution
        try:
            diagnosis_results = [
                {
                    "disease_id": disease_id,
                    "disease_name": result["disease"].disease_name,
                    "certainty": round(result["certainty"] * 100, 2)
                }
                for disease_id, result in sorted_conclusions.items()
            ]
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
    
    # @staticmethod
    # def explain_disease(disease_id: int, rule_trace: Dict[str, List[dict]]) -> List[dict]:
    #     # Make sure ID is string (keys in rule_trace are strings)
    #     disease_id = str(disease_id)

    #     return rule_trace.get(disease_id, [])
    @staticmethod
    def explain_disease(disease_id: int, rule_trace: Dict[str, List[dict]]) -> List[dict]:
        """
        Retrieves and sanitizes rule logs for a given disease ID.
        Ensures numerical values (cf_before, rule_cf, cf_after) are non-null floats.
        """
        if not rule_trace:
            return []

        # Check for both string and integer key representations
        str_id = str(disease_id)
        int_id = int(disease_id) if str_id.isdigit() else disease_id
        
        logs = rule_trace.get(str_id) or rule_trace.get(int_id) or []

        sanitized_logs = []
        for log in logs:
            sanitized_logs.append({
                "rule_id": log.get("rule_id", "N/A"),
                "matched": log.get("matched", []),
                "cf_before": float(log.get("cf_before", 0.0) or 0.0),
                "rule_cf": float(log.get("rule_cf", 0.0) or 0.0),
                "cf_after": float(log.get("cf_after", 0.0) or 0.0),
                "explanation": log.get("explanation", "")
            })

        return sanitized_logs

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