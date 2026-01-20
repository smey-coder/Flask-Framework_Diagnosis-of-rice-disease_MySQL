from typing import Dict, List, Set, Tuple
from app.models.rules import RulesTable
from app.models.diseases import DiseaseTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.symptoms import SymptomsTable
from app.models.treatments import TreatmentTable
from app.models.preventions import PreventionTable


class DiagnosisService:
    """
    Expert system service using MYCIN certainty factor.
    Supports partial matches and explanation logs.
    """

    @staticmethod
    def combine_cfs(cf1: float, cf2: float) -> float:
        """Combine two certainty factors using MYCIN formula."""
        if cf1 >= 0 and cf2 >= 0:
            result = cf1 + cf2 * (1 - cf1)
        elif cf1 < 0 and cf2 < 0:
            result = cf1 + cf2 * (1 + cf1)
        else:
            result = (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
        # Cap CF to [-0.99, 0.99] for safety
        return max(min(result, 0.99), -0.99)

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
                rule_cf = float(getattr(rule, "certainty", 0))  # fixed typo from 'certianty'
                adjusted_cf = rule_cf * (matched_count / total_count)

                if disease.id not in conclusions:
                    conclusions[disease.id] = {"disease": disease, "certainty": 0.0}
                    rule_trace[str(disease.id)] = []

                prev_cf = conclusions[disease.id]["certainty"]
                new_cf = cls.combine_cfs(prev_cf, adjusted_cf)
                conclusions[disease.id]["certainty"] = new_cf

                matched_names = [symptoms[sid].symptom_name for sid in matched_ids if sid in symptoms]

                rule_trace[str(disease.id)].append({
                    "rule_id": rule.id,
                    "rule_cf": round(adjusted_cf, 3),
                    "cf_before": round(prev_cf, 3),
                    "cf_after": round(new_cf, 3),
                    "explanation": getattr(rule, "explanation", ""),
                    "matched": matched_names
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

        return sorted_conclusions, rule_trace, skipped_rules

    @staticmethod
    def explain_disease(disease_id: int, rule_trace: Dict[str, List[dict]]) -> List[dict]:
        """Return explanation for a disease based on applied rules."""
        return rule_trace.get(str(disease_id), [])

    # ---- Backward compatible: allow optional rule_trace argument ----
    @staticmethod
    def treatment_disease(disease_id: int, rule_trace=None) -> List[dict]:
        """Return treatments for a disease."""
        treatments = TreatmentTable.query.filter_by(disease_id=disease_id, is_active=True).all()
        return [
            {"id": t.id, "method": t.method, "description": t.description, "image": t.image}
            for t in treatments
        ]

    @staticmethod
    def prevention_disease(disease_id: int, rule_trace=None) -> List[dict]:
        """Return preventions for a disease."""
        preventions = PreventionTable.query.filter_by(disease_id=disease_id, is_active=True).all()
        return [{"id": p.id, "description": p.description} for p in preventions]
