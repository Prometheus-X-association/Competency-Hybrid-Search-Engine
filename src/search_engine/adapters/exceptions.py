class AdapterError(Exception):
    """Base class for all adapter-related errors."""


class DBAdapterError(AdapterError):
    """Base class for database adapter errors."""


class CollectionCreationError(DBAdapterError):
    """Raised when a Qdrant collection cannot be created or checked for existence."""


class DBConnectionError(DBAdapterError):
    """Raised when connection to the database fails."""


class RepositoryError(DBAdapterError):
    """Raised when a Qdrant operation fails in the repository."""


class EmbeddingAdapterError(AdapterError):
    """Raised when an embedding operation fails."""


class EncodingError(EmbeddingAdapterError):
    """Raised when encoding fails, typically in the embedding service."""


class ModelLoadingError(EmbeddingAdapterError):
    """Raised when an embedding model fails to load."""
