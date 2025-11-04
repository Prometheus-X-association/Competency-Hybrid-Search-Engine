from dataclasses import dataclass

from domain.types.competency import Competency
from domain.types.identifier import Identifier
from domain.types.vectors import DenseVector, SparseVector


@dataclass
class Entity:
    """Entity in the search engine."""

    identifier: Identifier
    competency: Competency
    dense_vector: DenseVector | None = None
    sparse_vector: SparseVector | None = None
