# simulator/utils.py


def get_alignment_color(score):
    """Return color code for alignment score."""
    if score >= 0.95:
        return "green"
    elif score >= 0.7:
        return "yellow"
    return "red"

def anonymize_log(log):
    import re
    text = re.sub(r"[\w.-]+@[\w.-]+", "[REDACTED_EMAIL]", log)
    text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[REDACTED_CREDIT_CARD]", text)
    return text
