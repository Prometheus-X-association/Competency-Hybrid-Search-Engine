from dataclasses import dataclass
from enum import StrEnum


@dataclass
class DenseVector:
    """Dataclass representing a dense vector."""

    values: list[float]


@dataclass
class SparseVector:
    """Dataclass representing a sparse vector with indices and values."""

    indices: list[int]
    values: list[float]


class VectorName(StrEnum):
    """Enum for vector names used in the search engine."""

    DENSE = "dense"
    SPARSE = "sparse"
