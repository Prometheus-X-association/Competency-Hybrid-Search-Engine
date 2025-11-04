from abc import ABC, abstractmethod
from collections.abc import Sequence

from domain.types.entity import Entity
from domain.types.filters import DomainFilter
from domain.types.identifier import Identifier
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import DenseVector, SparseVector, VectorName


class RepositoryContract(ABC):
    """Contract for repository services."""

    @abstractmethod
    def create_entity(self, model: CreateEntityModel) -> Entity:
        """Creates a new entity in Qdrant.

        Args:
            model (CreateEntityModel): CreateEntityModel with `competency` and `vector`.

        Returns:
            Entity: The created entity with a generated identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def get_entity(self, identifier: Identifier) -> Entity | None:
        """Retrieves an entity by its identifier.

        Args:
            identifier (Identifier): The UUID of the entity.

        Returns:
            Entity | None: The found entity or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def update_entity(self, model: UpdateEntityModel) -> Entity:
        """Updates an existing entity (competency + vector).

        Args:
            model (UpdateEntityModel): UpdateEntityModel with `id`,
                `competency`, and `vector`.

        Returns:
            Entity: The updated entity.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_entity(self, identifier: Identifier) -> None:
        """Deletes an entity from Qdrant by its identifier.

        Args:
            identifier (Identifier): The UUID of the entity to delete.
        """
        raise NotImplementedError

    @abstractmethod
    def search_by_vector_and_filters(
        self,
        vector: DenseVector | SparseVector,
        filters: Sequence[DomainFilter],
        top: int,
        vector_name: VectorName = VectorName.DENSE,
    ) -> Sequence[SearchResult]:
        """Searches for similar entities to a given vector with filter criteria.

        Args:
            vector (DenseVector | SparseVector): The vector to search for.
            filters (Sequence[DomainFilter]): The filters criteria to apply.
            top (int): The number of results to return.
            vector_name (VectorName): The name of the vector to search with.

        Returns:
            Sequence[SearchResult]: A sequence of SearchResult objects.
        """
        raise NotImplementedError

    @abstractmethod
    def search_hybrid_by_vectors_and_filters(
        self,
        dense_vector: DenseVector,
        sparse_vector: SparseVector,
        filters: Sequence[DomainFilter],
        top: int,
    ) -> Sequence[SearchResult]:
        """Searches using hybrid approach combining dense and sparse vectors.

        Args:
            dense_vector (DenseVector): The dense vector for semantic search.
            sparse_vector (SparseVector): The sparse vector for keyword search.
            filters (Sequence[DomainFilter]): The filters criteria to apply.
            top (int): The number of results to return.

        Returns:
            Sequence[SearchResult]: A sequence of SearchResult objects with
                hybrid scoring.
        """
        raise NotImplementedError
