


class ArricFetcherBaseError(Exception):
    """Base class for all exceptions in artic fetcher."""
    def __init__(self, message: str | None = None):
        self.message = message or "A arric fetcher error occurred."
        super().__init__(self.message)

class ArticPlaceNotFoundError(ArricFetcherBaseError):
    """Raised when a specific artic place ID is not found."""
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Artic place with ID '{name}' could not be found.")