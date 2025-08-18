# custos/training.py

class FeedbackTrainer:
    def __init__(self):
        self.logs = []

    def record_violation(self, context: dict, violations: list):
        log = {
            "prompt": context["prompt"],
            "response": context["response"],
            "violations": violations,
            "source": context.get("metadata", {}).get("source", "unknown")
        }
        self.logs.append(log)
        print("[CUSTOS] Violation Recorded:", log)
