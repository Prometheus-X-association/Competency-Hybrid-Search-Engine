from collections.abc import Sequence

from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.contracts.repository import (
    RepositoryContract,
)
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.exceptions import (
    EmbeddingError,
    EntityNotFoundError,
    ValidationError,
)
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.filters import DomainFilter
from domain.types.identifier import Identifier
from domain.types.search_type import SearchType
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import VectorName


class EntityService:
    """Service for managing entities in the search engine."""

    def __init__(
        self,
        repository: RepositoryContract,
        dense_embedding_service: EmbeddingServiceContract,
        sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Initialize the EntityService.

        Args:
            repository (RepositoryContract): The repository contract for data access.
            dense_embedding_service (EmbeddingServiceContract):
                The dense embedding service contract for text encoding.
            sparse_embedding_service (SparseEmbeddingServiceContract):
                The sparse embedding service contract for text encoding.
        """
        self.repository = repository
        self.dense_embedding_service = dense_embedding_service
        self.sparse_embedding_service = sparse_embedding_service

    def create_entity(self, competency: Competency, text: str | None) -> Entity:
        """Creates a new entity in the search engine.

        Args:
            competency (Competency): The competency data to create the entity.
            text (str | None): The text to encode into a vector.

        Raises:
            ValidationError: If the text to encode is not provided.
            EmbeddingError: If the encoding fails.

        Returns:
            Entity: The created entity.
        """
        text = text.strip() if text else None
        if not text:
            raise ValidationError("Text cannot be empty.")

        try:
            dense_vector = self.dense_embedding_service.encode(text=text)
            sparse_vector = self.sparse_embedding_service.encode(text=text)
        except Exception as e:
            raise EmbeddingError(f"Encoding error: {e}") from e

        # Create the entity using both vectors
        model = CreateEntityModel(
            competency=competency,
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
        )
        return self.repository.create_entity(model=model)

    def get_entity(self, identifier: Identifier) -> Entity:
        """Retrieves an entity by its identifier.

        Args:
            identifier (Identifier): The identifier of the entity to retrieve.

        Raises:
            EntityNotFoundError: If the entity with the given identifier does not exist.

        Returns:
            Entity: The retrieved entity.
        """
        entity = self.repository.get_entity(identifier=identifier)
        if entity is None:
            raise EntityNotFoundError(f"Entity {identifier} not found")
        return entity

    def update_entity(
        self,
        identifier: Identifier,
        competency: Competency,
        text: str | None,
    ) -> Entity:
        """Updates an existing entity in the search engine.

        Args:
            identifier (Identifier): The identifier of the entity to update.
            competency (Competency): The new competency data for the entity.
            text (str | None): The text to encode into a vector.

        Raises:
            ValidationError: If the text to encode is not provided.
            ValidationError: If neither competency nor text is provided.
            EmbeddingError: If the encoding fails.

        Returns:
            Entity: The updated entity.
        """
        entity = self.get_entity(identifier=identifier)

        # If no text is provided or if it is the same as the existing one,
        # use the existing vector.
        if text is None or entity.competency.indexed_text == text:
            dense_vector = entity.dense_vector
            sparse_vector = entity.sparse_vector
        else:
            # Ensure the text is not empty
            text = text.strip()
            if not text:
                raise ValidationError("Text cannot be empty.")

            # Encode the text to vectors
            try:
                dense_vector = self.dense_embedding_service.encode(text=text)
                sparse_vector = self.sparse_embedding_service.encode(text=text)
            except Exception as e:
                raise EmbeddingError(f"Encoding error: {e}") from e

        model = UpdateEntityModel(
            identifier=identifier,
            competency=competency,
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
        )
        return self.repository.update_entity(model=model)

    def delete_entity(self, identifier: Identifier) -> None:
        """Deletes an entity from the search engine.

        Args:
            identifier (Identifier): The identifier of the entity to delete.
        """
        self.get_entity(identifier=identifier)

        self.repository.delete_entity(identifier=identifier)

    def search_by_text_and_filters_with_type(
        self,
        text: str,
        filters: Sequence[DomainFilter],
        top: int,
        search_type: SearchType = SearchType.SEMANTIC,
    ) -> Sequence[SearchResult]:
        """Search for entities with specific search type and additional payload filters.

        Args:
            text (str): The text to encode and search for similar entities.
            filters (Sequence[DomainFilter]): Additional filters to apply to the search.
            top (int): The number of neighbors to return.
            search_type (SearchType): The type of search to perform.

        Raises:
            ValidationError: If the text to encode is empty.
            EmbeddingError: If the encoding fails.

        Returns:
            Sequence[SearchResult]: A sequence of SearchResult objects,
            containing the found entities and their scores.
        """
        # Ensure the text is not empty
        text = text.strip()
        if not text:
            raise ValidationError("Searched text cannot be empty.")

        if search_type == SearchType.SEMANTIC:
            try:
                dense_vector = self.dense_embedding_service.encode(text)
            except Exception as e:
                raise EmbeddingError(f"Dense encoding error: {e}") from e

            return self.repository.search_by_vector_and_filters(
                vector=dense_vector,
                filters=filters,
                top=top,
                vector_name=VectorName.DENSE,
            )

        if search_type == SearchType.SPARSE:
            try:
                sparse_vector = self.sparse_embedding_service.encode(text)
            except Exception as e:
                raise EmbeddingError(f"Sparse encoding error: {e}") from e

            return self.repository.search_by_vector_and_filters(
                vector=sparse_vector,
                filters=filters,
                top=top,
                vector_name=VectorName.SPARSE,
            )

        if search_type == SearchType.HYBRID:
            try:
                dense_vector = self.dense_embedding_service.encode(text)
                sparse_vector = self.sparse_embedding_service.encode(text)
            except Exception as e:
                raise EmbeddingError(f"Encoding error: {e}") from e

            return self.repository.search_hybrid_by_vectors_and_filters(
                dense_vector=dense_vector,
                sparse_vector=sparse_vector,
                filters=filters,
                top=top,
            )

        raise ValidationError(f"Unsupported search type: {search_type}")
