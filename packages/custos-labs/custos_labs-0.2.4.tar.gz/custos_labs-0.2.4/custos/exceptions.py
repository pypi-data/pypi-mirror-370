### custos/exceptions.py

class AlignmentViolation(Exception):
    """Raised when alignment rules are violated."""
    def __init__(self, message, result=None):
        super().__init__(message)
        self.result = result or {}
