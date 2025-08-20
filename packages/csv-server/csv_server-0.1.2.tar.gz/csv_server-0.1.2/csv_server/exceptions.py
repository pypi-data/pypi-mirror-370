"""Custom exceptions for csv-server."""


class CSVServerError(Exception):
    """Base exception for csv-server."""
    pass


class ValidationError(CSVServerError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, errors: list = None):
        super().__init__(message)
        self.errors = errors or []


class ResourceNotFoundError(CSVServerError):
    """Raised when a requested resource is not found."""
    pass


class ConfigurationError(CSVServerError):
    """Raised when there's an error in configuration."""
    pass


class StorageError(CSVServerError):
    """Raised when there's an error with storage operations."""
    pass