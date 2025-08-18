class AppException(Exception):
    """Base class untuk semua custom exception di aplikasi."""

    def __init__(self, message="Application error", code=500):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.message}"
