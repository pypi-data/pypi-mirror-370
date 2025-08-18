### custos/utils.py

def redact_sensitive(text: str) -> str:
    import re
    text = re.sub(r"[\w.-]+@[\w.-]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[REDACTED_CREDIT_CARD]", text)
    return text