# test_diagnosis_service.py
from app.services.diagnosis_service import DiagnosisService
from app.models.symptoms import SymptomsTable
from app.models.rules import RulesTable
from app.models.rule_conditions import RuleConditionsTable
from app.models.diseases import DiseaseTable
from app import db  # if using SQLAlchemy

def test_diagnosis():
    """
    Test DiagnosisService with example symptoms and rules.
    """

    # Example: Insert mock symptoms (if your DB is empty)
    # comment out if already populated
    symptom1 = SymptomsTable(symptom_name="Yellow Leaves", is_active=True)
    symptom2 = SymptomsTable(symptom_name="Brown Spots", is_active=True)
    symptom3 = SymptomsTable(symptom_name="Wilting", is_active=True)
    db.session.add_all([symptom1, symptom2, symptom3])
    db.session.commit()

    # Example: Insert diseases
    disease1 = DiseaseTable(disease_name="Rice Blast", is_active=True)
    disease2 = DiseaseTable(disease_name="Bacterial Leaf Blight", is_active=True)
    db.session.add_all([disease1, disease2])
    db.session.commit()

    # Example: Insert rules
    rule1 = RulesTable(disease_id=disease1.id, certainty=0.9, explanation="Blast causes leaf spots", is_active=True)
    rule2 = RulesTable(disease_id=disease2.id, certainty=0.8, explanation="Blight causes yellow leaves", is_active=True)
    db.session.add_all([rule1, rule2])
    db.session.commit()

    # Example: Insert rule conditions
    cond1 = RuleConditionsTable(rule_id=rule1.id, symptom_id=symptom2.id, is_active=True)
    cond2 = RuleConditionsTable(rule_id=rule1.id, symptom_id=symptom3.id, is_active=True)
    cond3 = RuleConditionsTable(rule_id=rule2.id, symptom_id=symptom1.id, is_active=True)
    db.session.add_all([cond1, cond2, cond3])
    db.session.commit()

    # ✅ Selected symptoms by user (simulate input)
    selected_symptom_ids = [symptom1.id, symptom2.id]

    # Initialize the service
    service = DiagnosisService()

    # Run inference
    conclusions, rule_trace, skipped_rules = service.infer(selected_symptom_ids)

    # Print results
    print("\n=== DIAGNOSIS RESULTS ===")
    if conclusions:
        for disease_id, data in conclusions.items():
            print(f"Disease: {data['disease'].disease_name}")
            print(f"Certainty: {data['certainty']*100:.1f}%")
            print(f"Rules Applied: {len(data)}")
    else:
        print("No matching diseases found.")

    print("\n=== RULE TRACE ===")
    for disease_id, logs in rule_trace.items():
        print(f"Disease ID {disease_id}:")
        for log in logs:
            print(f"  Rule {log['rule_id']}: matched {log['matched']}, CF after: {log['cf_after']}")

    print("\n=== SKIPPED RULES ===")
    for skipped in skipped_rules:
        print(f"Rule {skipped['rule_id']} skipped, missing: {skipped['missing']}")


if __name__ == "__main__":
    test_diagnosis()
