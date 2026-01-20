from typing import Optional, List, Dict, Tuple, Set
from extensions import db


class EngineService:
    # ================= CERTAINTY FACTOR =================
    @staticmethod
    def combine_cfs(cf1: float, cf2: float) -> float:
        """Combine two certainty factors (MYCIN formula)."""
        return cf1 + cf2 * (1.0 - cf1)

    # ================= FETCH RULES (RAW SQL) =================
    @staticmethod
    def fetch_all_rules() -> List[Dict]:
        """
        Load all rules and their conditions using SQL statements.
        """
        sql = """
            SELECT
                r.rule_id,
                r.disease_id,
                d.name AS disease_name,
                r.certainty,
                r.explanation,
                r.image,
                rc.symptom_code
            FROM rules r
            JOIN diseases d ON r.disease_id = d.disease_id
            LEFT JOIN rule_conditions rc ON r.rule_id = rc.rule_id
            ORDER BY r.rule_id
        """

        result = db.session.execute(db.text(sql)).fetchall()

        rules_dict: Dict[int, Dict] = {}

        for row in result:
            rid = row.rule_id

            if rid not in rules_dict:
                rules_dict[rid] = {
                    "rule_id": rid,
                    "disease_id": row.disease_id,
                    "disease_name": row.disease_name,
                    "conditions": set(),
                    "certainty": float(row.certainty),
                    "explanation": row.explanation,
                    "image": row.image,
                }

            if row.symptom_code:
                rules_dict[rid]["conditions"].add(row.symptom_code)

        return list(rules_dict.values())

    # ================= FETCH SYMPTOMS =================
    @staticmethod
    def fetch_all_symptoms() -> List[Dict]:
        sql = """
            SELECT symptom_id, code, name
            FROM symptoms
            ORDER BY symptom_id
        """

        rows = db.session.execute(db.text(sql)).fetchall()

        return [
            {"id": r.symptom_id, "code": r.code, "name": r.name}
            for r in rows
        ]

    # ================= FETCH TREATMENTS =================
    @staticmethod
    def fetch_treatments(disease_id: str) -> List[str]:
        sql = """
            SELECT method
            FROM treatments
            WHERE disease_id = :disease_id
        """

        rows = db.session.execute(
            db.text(sql),
            {"disease_id": disease_id}
        ).fetchall()

        return [r.method for r in rows]

    # ================= INFERENCE ENGINE =================
    @staticmethod
    def infer(
        facts: Set[str],
    ) -> Tuple[Dict[str, Dict], Dict[str, List[Dict]], List[Dict]]:
        """
        Infer diseases based on selected symptoms.
        """
        rules = EngineService.fetch_all_rules()

        conclusions: Dict[str, Dict] = {}
        rule_trace: Dict[str, List[Dict]] = {}
        skipped_rules: List[Dict] = []

        for rule in rules:
            conditions = rule["conditions"]

            if conditions.issubset(facts):
                disease_id = rule["disease_id"]
                cf = rule["certainty"]

                trace = {
                    "rule": rule["rule_id"],
                    "cf": cf,
                    "explanation": rule["explanation"],
                    "image": rule["image"],
                }

                if disease_id in conclusions:
                    conclusions[disease_id]["certainty"] = EngineService.combine_cfs(
                        conclusions[disease_id]["certainty"], cf
                    )
                    rule_trace[disease_id].append(trace)
                else:
                    conclusions[disease_id] = {
                        "disease_name": rule["disease_name"],
                        "certainty": cf,
                        "image": rule["image"],
                    }
                    rule_trace[disease_id] = [trace]
            else:
                skipped_rules.append(
                    {
                        "rule": rule["rule_id"],
                        "missing": list(conditions - facts),
                        "disease": rule["disease_name"],
                    }
                )

        return conclusions, rule_trace, skipped_rules

    # ================= EXPLANATION =================
    @staticmethod
    def explain(
        disease_id: str, rule_trace: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Explain certainty factor calculation step-by-step.
        """
        if disease_id not in rule_trace:
            return {"error": "Disease not found in trace."}

        cf_val = 0.0
        steps = []

        for r in rule_trace[disease_id]:
            prev_cf = cf_val
            cf_val = EngineService.combine_cfs(cf_val, r["cf"])

            steps.append(
                {
                    "rule": r["rule"],
                    "rule_cf": r["cf"],
                    "cf_before": round(prev_cf, 3),
                    "cf_after": round(cf_val, 3),
                    "explanation": r["explanation"],
                    "image": r.get("image"),
                }
            )

        return {
            "disease_id": disease_id,
            "certainty": round(cf_val, 3),
            "supporting_rules": steps,
        }
