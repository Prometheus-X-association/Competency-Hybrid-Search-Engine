from enum import StrEnum


class SearchType(StrEnum):
    """Enum for search types."""

    SEMANTIC = "semantic"  # Dense embeddings (existing)
    SPARSE = "sparse"  # Sparse embeddings
    HYBRID = "hybrid"  # Combination of both
