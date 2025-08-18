# custos/policy.py

class AlignmentPolicyEngine:
    def __init__(self, registry):
        self.registry = registry
        self._banned = [
            r"\bbomb\b", r"\bhack\b", r"\bmalware\b", r"\bfentanyl\b",
            r"\bcredit\s*card\b", r"\bdoxx?\b",
        ]

    def evaluate(self, context: dict) -> list:
        violations = []

        ethics = context["ethics"]
        prompt = context["prompt"]
        response = context["response"]


        if ethics["do_no_harm"] and ("encourage violence" in response.lower()):
            violations.append("Harmful recommendation")

        if ethics["transparency"] and ("I am not allowed to explain" in response.lower()):
            violations.append("Lack of transparency")

        # Expand with registry rules
        registry_rules = self.registry.get_active_policies()
        for rule in registry_rules:
            if rule in response.lower():
                violations.append(f"Violation of policy: {rule}")

        return violations