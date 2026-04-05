from typing import Set, Dict, List, Tuple
from extensions import db

# ===================== Notes =================================================#
# Inference Engine for Rice Disease Expert System using raw SQL
#==============================================================================#

# ================= DATABASE HELPERS =================
def get_db_connection():
    """Return a raw database connection."""
    conn = db.engine.connect()
    return conn

# ================= FETCH FUNCTIONS =================
def fetch_all_rules() -> List[dict]:
    """Load all active rules with their conditions using raw SQL."""
    try:
        conn = get_db_connection()
        # Get all active rules with disease info
        rules_sql = """
        SELECT r.id AS rule_id, r.disease_id, r.certianty AS certainty, 
               r.explanation, r.image, d.disease_name
        FROM tbl_rules r
        JOIN tbl_diseases d ON r.disease_id = d.id
        WHERE r.is_active = 1 AND d.is_active = 1
        """
        result = conn.execute(rules_sql)
        rules = []
        for row in result:
            # Fetch all active conditions for this rule
            cond_sql = """
            SELECT symptom_id
            FROM tbl_rule_conditions
            WHERE rule_id = :rule_id AND is_active = 1
            """
            cond_result = conn.execute(cond_sql, {"rule_id": row["rule_id"]})
            conditions = {c["symptom_id"] for c in cond_result}

            rules.append({
                "rule_id": row["rule_id"],
                "disease_id": row["disease_id"],
                "disease_name": row["disease_name"],
                "conditions": conditions,
                "certainty": float(row["certainty"]),
                "explanation": row["explanation"] or "",
                "image": row["image"] or ""
            })
        conn.close()
        return rules
    except Exception as e:
        print(f"[engine.py] Error fetching rules: {e}")
        return []

def fetch_all_symptoms() -> List[dict]:
    """Fetch all active symptoms using raw SQL."""
    try:
        conn = get_db_connection()
        sql = "SELECT id, code, symptom_name FROM tbl_symptoms WHERE is_active = 1 ORDER BY id"
        result = conn.execute(sql)
        symptoms = [{"id": r["id"], "code": r["code"], "name": r["symptom_name"]} for r in result]
        conn.close()
        return symptoms
    except Exception as e:
        print(f"[engine.py] Error fetching symptoms: {e}")
        return []

def fetch_treatments(disease_id: int) -> List[str]:
    """Fetch all active treatments for a disease using raw SQL."""
    try:
        conn = get_db_connection()
        sql = """
        SELECT method, treatment_type
        FROM tbl_treatments
        WHERE disease_id = :disease_id AND is_active = 1
        """
        result = conn.execute(sql, {"disease_id": disease_id})
        treatments = []
        for row in result:
            if row["method"]:
                treatments.append(row["method"])
            elif row["treatment_type"]:
                treatments.append(row["treatment_type"])
        conn.close()
        return treatments
    except Exception as e:
        print(f"[engine.py] Error fetching treatments: {e}")
        return []

# ================= CERTAINTY FACTOR =================
def combine_cfs(cf1: float, cf2: float) -> float:
    """Combine two certainty factors using MYCIN formula."""
    return cf1 + cf2 * (1.0 - cf1)

# ================= INFERENCE ENGINE =================
def infer(facts: Set[str]) -> Tuple[Dict[int, dict], Dict[int, List[dict]], List[dict]]:
    rules = fetch_all_rules()
    conclusions: Dict[int, dict] = {}
    rule_trace: Dict[int, List[dict]] = {}
    skipped_rules: List[dict] = []

    for rule in rules:
        conds = rule["conditions"]
        if conds.issubset(facts):
            disease_id = rule["disease_id"]
            cf = rule["certainty"]
            trace_entry = {
                "rule": rule["rule_id"],
                "cf": cf,
                "explanation": rule["explanation"],
                "image": rule["image"]
            }
            if disease_id in conclusions:
                conclusions[disease_id]["certainty"] = combine_cfs(conclusions[disease_id]["certainty"], cf)
                rule_trace[disease_id].append(trace_entry)
            else:
                conclusions[disease_id] = {
                    "disease_name": rule["disease_name"],
                    "certainty": cf,
                    "image": rule["image"]
                }
                rule_trace[disease_id] = [trace_entry]
        else:
            skipped_rules.append({
                "rule": rule["rule_id"],
                "missing": list(conds - facts),
                "disease": rule["disease_name"]
            })

    return conclusions, rule_trace, skipped_rules

# ================= EXPLANATION =================
def explain(disease_id: int, rule_trace: Dict[int, List[dict]]) -> dict:
    if disease_id not in rule_trace:
        return {"error": "Disease not found in trace."}

    support = rule_trace[disease_id]
    cf_val = 0.0
    steps = []

    for r in support:
        prev_cf = cf_val
        cf_val = combine_cfs(cf_val, r["cf"])
        steps.append({
            "rule": r["rule"],
            "rule_cf": r["cf"],
            "cf_before": round(prev_cf, 3),
            "cf_after": round(cf_val, 3),
            "explanation": r["explanation"],
            "image": r.get("image")
        })

    return {
        "disease_id": disease_id,
        "certainty": round(cf_val, 3),
        "supporting_rules": steps
    }
