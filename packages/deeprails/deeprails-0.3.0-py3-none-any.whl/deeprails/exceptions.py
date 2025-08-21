class DeepRailsError(Exception):
    """Base exception class for the DeepRails SDK."""
    pass

class DeepRailsAPIError(DeepRailsError):
    """Raised when the DeepRails API returns an error."""
    def __init__(self, status_code: int, error_detail: str):
        self.status_code = status_code
        self.error_detail = error_detail
        super().__init__(f"API Error {status_code}: {error_detail}")