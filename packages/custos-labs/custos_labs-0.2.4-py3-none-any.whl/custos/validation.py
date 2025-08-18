### custos/validation.py

from custos.exceptions import AlignmentViolation

class Validator:
    def check(self, prompt: str, response: str, policy: dict) -> list:
        violations = []
        for rule in policy.get("rules", []):
            if rule["type"] == "harmful" and (rule["keyword"] in prompt.lower() or rule["keyword"] in response.lower()):
                violations.append(rule["label"])
            if rule["type"] == "misinfo" and rule["keyword"] in response.lower():
                violations.append("misinformation")

        if violations:
            raise AlignmentViolation(f"Detected alignment issues: {violations}")

        return violations