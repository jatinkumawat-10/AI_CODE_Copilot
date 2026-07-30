class LLMServiceError(Exception):
    """
    Raised when communication with the LLM fails. Carries a status_code so
    the exception handler can return a meaningful HTTP status instead of a
    hardcoded 500 for every failure type (rate limit, provider outage, or
    a genuine internal bug are meaningfully different situations).
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
