### custos/monitor.py

class Monitor:
    _suspicious = ["ignore safety", "bypass", "workaround", "jailbreak", "secret"]

    def analyze(self, prompt: str, response: str):
        hay = f"{prompt} {response}".lower()
        flags = [kw for kw in self._suspicious if kw in hay]
        return {"suspicious_keywords": flags}
