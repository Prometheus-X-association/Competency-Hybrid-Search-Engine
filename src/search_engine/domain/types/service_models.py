from dataclasses import dataclass

from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.identifier import Identifier
from domain.types.vectors import DenseVector, SparseVector


@dataclass
class SearchResult:
    """Represents a search result."""

    entity: Entity
    score: float


@dataclass
class CreateEntityModel:
    """Model for creating an entity."""

    competency: Competency
    dense_vector: DenseVector
    sparse_vector: SparseVector


@dataclass
class UpdateEntityModel:
    """Model for updating an entity."""

    identifier: Identifier
    competency: Competency
    dense_vector: DenseVector
    sparse_vector: SparseVector
