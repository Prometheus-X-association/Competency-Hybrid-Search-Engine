class DomainError(Exception):
    """Base class for all domain-related errors."""


class EmbeddingError(DomainError):
    """Raised when embedding fails."""


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found by its ID."""


class ValidationError(DomainError):
    """Raised for data validation errors."""
