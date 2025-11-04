"""Test module for EntityService."""

from uuid import uuid4

import pytest

from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.contracts.repository import RepositoryContract
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.exceptions import (
    EmbeddingError,
    EntityNotFoundError,
    ValidationError,
)
from domain.services.entity_service import EntityService
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.search_type import SearchType
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
)
from domain.types.vectors import DenseVector, SparseVector


class TestEntityService:
    """Test class for EntityService."""

    # Init
    def test_entity_service_initialization(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EntityService initialization."""
        service = EntityService(
            repository=mock_repository,
            dense_embedding_service=mock_embedding_service,
            sparse_embedding_service=mock_sparse_embedding_service,
        )

        assert service.repository == mock_repository
        assert service.dense_embedding_service == mock_embedding_service
        assert service.sparse_embedding_service == mock_sparse_embedding_service

    def test_entity_service_initialization_missing_input_variables(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EntityService initialization missing input variables."""
        with pytest.raises(TypeError):
            EntityService()

        with pytest.raises(TypeError):
            EntityService(repository=mock_repository)

        with pytest.raises(TypeError):
            EntityService(dense_embedding_service=mock_embedding_service)

        with pytest.raises(TypeError):
            EntityService(sparse_embedding_service=mock_sparse_embedding_service)

        with pytest.raises(TypeError):
            EntityService(
                repository=mock_repository,
                dense_embedding_service=mock_embedding_service,
            )

        with pytest.raises(TypeError):
            EntityService(
                repository=mock_repository,
                sparse_embedding_service=mock_sparse_embedding_service,
            )

        with pytest.raises(TypeError):
            EntityService(
                dense_embedding_service=mock_embedding_service,
                sparse_embedding_service=mock_sparse_embedding_service,
            )

    # Create Entity
    def test_create_entity_success(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
    ) -> None:
        """Test successful entity creation."""
        # Setup mocks
        text = "Test text for embedding"

        mock_embedding_service.encode.return_value = sample_entity.dense_vector
        mock_sparse_embedding_service.encode.return_value = sample_entity.sparse_vector
        mock_repository.create_entity.return_value = sample_entity

        # Execute
        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )
        result = service.create_entity(sample_entity.competency, text)
        expected_output_model = CreateEntityModel(
            competency=sample_entity.competency,
            dense_vector=sample_entity.dense_vector,
            sparse_vector=sample_entity.sparse_vector,
        )

        # Verify
        assert result == sample_entity
        mock_embedding_service.encode.assert_called_once_with(text=text)
        mock_sparse_embedding_service.encode.assert_called_once_with(text=text)

        # Verify the create_entity call
        mock_repository.create_entity.assert_called_once_with(
            model=expected_output_model,
        )

    def test_create_entity_empty_text_validation(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_competency: Competency,
    ) -> None:
        """Test ValidationError for empty text."""
        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        # Test with empty string
        with pytest.raises(ValidationError):
            service.create_entity(sample_competency, "")

        # Test with None
        with pytest.raises(ValidationError):
            service.create_entity(sample_competency, None)

        # Test with whitespace only
        with pytest.raises(ValidationError):
            service.create_entity(sample_competency, "   ")

        # Verify embedding service was not called
        mock_embedding_service.encode.assert_not_called()
        mock_sparse_embedding_service.encode.assert_not_called()
        mock_repository.create_entity.assert_not_called()

    def test_create_entity_encoding_error(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_competency: Competency,
    ) -> None:
        """Test EmbeddingError when encoding fails."""
        text = "Test text"

        # Setup encoding error
        mock_embedding_service.encode.side_effect = Exception("Encoding failed")

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        # Should raise EmbeddingError
        with pytest.raises(EmbeddingError):
            service.create_entity(sample_competency, text)

        # Verify embedding service was called but repository was not
        mock_embedding_service.encode.assert_called_once_with(text=text)
        mock_repository.create_entity.assert_not_called()

    # Get Entity
    def test_get_entity_success(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
    ) -> None:
        """Test successful entity retrieval."""
        mock_repository.get_entity.return_value = sample_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )
        result = service.get_entity(sample_entity.identifier)

        assert result == sample_entity
        mock_repository.get_entity.assert_called_once_with(
            identifier=sample_entity.identifier,
        )

    def test_get_entity_not_found(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EntityNotFoundError when entity doesn't exist."""
        identifier = uuid4()
        mock_repository.get_entity.return_value = None

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(EntityNotFoundError):
            service.get_entity(identifier)

        mock_repository.get_entity.assert_called_once_with(identifier=identifier)

    # Delete Entity
    def test_delete_entity_success(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
    ) -> None:
        """Test successful entity deletion."""
        mock_repository.get_entity.return_value = sample_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )
        service.delete_entity(sample_entity.identifier)

        mock_repository.get_entity.assert_called_once_with(
            identifier=sample_entity.identifier,
        )
        mock_repository.delete_entity.assert_called_once_with(
            identifier=sample_entity.identifier,
        )

    def test_delete_entity_not_found(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test deleting non-existent entity."""
        identifier = uuid4()
        mock_repository.get_entity.return_value = None

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(EntityNotFoundError):
            service.delete_entity(identifier)

        # Verify delete was not called
        mock_repository.delete_entity.assert_not_called()

    # Update Entity
    def test_update_entity_success(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test successful entity update with new text."""
        identifier = uuid4()
        new_text = "Updated text"
        updated_entity = Entity(
            identifier=identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )
        updated_entity.competency.code = "UPDATED_CODE"
        updated_entity.dense_vector.values.append(0.5)
        updated_entity.sparse_vector.indices.append(999)
        updated_entity.sparse_vector.values.append(0.75)

        mock_repository.get_entity.return_value = sample_entity
        mock_embedding_service.encode.return_value = sample_dense_vector
        mock_sparse_embedding_service.encode.return_value = sample_sparse_vector
        mock_repository.update_entity.return_value = updated_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )
        result = service.update_entity(identifier, sample_competency, new_text)

        assert result == updated_entity
        mock_repository.get_entity.assert_called_once_with(identifier=identifier)
        mock_embedding_service.encode.assert_called_once_with(text=new_text)
        mock_sparse_embedding_service.encode.assert_called_once_with(text=new_text)
        mock_repository.update_entity.assert_called_once()

    def test_update_entity_no_text_reuse_vectors(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
        sample_competency: Competency,
    ) -> None:
        """Test entity update without new text reuses existing vectors."""
        identifier = uuid4()

        mock_repository.get_entity.return_value = sample_entity
        mock_repository.update_entity.return_value = sample_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )
        result = service.update_entity(identifier, sample_competency, None)

        assert result == sample_entity
        mock_repository.get_entity.assert_called_once_with(identifier=identifier)
        mock_embedding_service.encode.assert_not_called()
        mock_sparse_embedding_service.encode.assert_not_called()
        mock_repository.update_entity.assert_called_once()

    def test_update_entity_empty_text_validation(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
        sample_competency: Competency,
    ) -> None:
        """Test ValidationError for empty text in update."""
        identifier = uuid4()

        mock_repository.get_entity.return_value = sample_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(ValidationError):
            service.update_entity(identifier, sample_competency, "")

        with pytest.raises(ValidationError):
            service.update_entity(identifier, sample_competency, "   ")

    def test_update_entity_encoding_error(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_entity: Entity,
        sample_competency: Competency,
    ) -> None:
        """Test EmbeddingError during update."""
        identifier = uuid4()
        new_text = "Updated text"

        mock_repository.get_entity.return_value = sample_entity

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        mock_sparse_embedding_service.encode.side_effect = Exception(
            "Sparse encoding failed",
        )
        with pytest.raises(EmbeddingError):
            service.update_entity(identifier, sample_competency, new_text)

        mock_embedding_service.encode.side_effect = Exception("Encoding failed")
        with pytest.raises(EmbeddingError):
            service.update_entity(identifier, sample_competency, new_text)

    # Search
    # NOTE: J'en suis ICI
    def test_search_by_text_semantic(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_dense_vector: DenseVector,
        sample_search_result: SearchResult,
    ) -> None:
        """Test semantic search."""
        text = "search text"
        filters = []
        top = 10

        mock_embedding_service.encode.return_value = sample_dense_vector
        mock_repository.search_by_vector_and_filters.return_value = [
            sample_search_result,
        ]

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        result = service.search_by_text_and_filters_with_type(
            text=text,
            filters=filters,
            top=top,
            search_type=SearchType.SEMANTIC,
        )

        assert result == [sample_search_result]
        mock_embedding_service.encode.assert_called_once_with(text)
        mock_repository.search_by_vector_and_filters.assert_called_once_with(
            vector=sample_dense_vector,
            filters=filters,
            top=top,
            vector_name="dense",
        )

    def test_search_by_text_sparse(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_sparse_vector: SparseVector,
        sample_search_result: SearchResult,
    ) -> None:
        """Test sparse search."""
        text = "search text"
        filters = []
        top = 10

        mock_sparse_embedding_service.encode.return_value = sample_sparse_vector
        mock_repository.search_by_vector_and_filters.return_value = [
            sample_search_result,
        ]

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        result = service.search_by_text_and_filters_with_type(
            text=text,
            filters=filters,
            top=top,
            search_type=SearchType.SPARSE,
        )

        assert result == [sample_search_result]
        mock_sparse_embedding_service.encode.assert_called_once_with(text)
        mock_repository.search_by_vector_and_filters.assert_called_once_with(
            vector=sample_sparse_vector,
            filters=filters,
            top=top,
            vector_name="sparse",
        )

    def test_search_by_text_hybrid(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
        sample_search_result: SearchResult,
    ) -> None:
        """Test hybrid search."""
        text = "search text"
        filters = []
        top = 10

        mock_embedding_service.encode.return_value = sample_dense_vector
        mock_sparse_embedding_service.encode.return_value = sample_sparse_vector
        mock_repository.search_hybrid_by_vectors_and_filters.return_value = [
            sample_search_result,
        ]

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        result = service.search_by_text_and_filters_with_type(
            text=text,
            filters=filters,
            top=top,
            search_type=SearchType.HYBRID,
        )

        assert result == [sample_search_result]
        mock_embedding_service.encode.assert_called_once_with(text)
        mock_sparse_embedding_service.encode.assert_called_once_with(text)
        mock_repository.search_hybrid_by_vectors_and_filters.assert_called_once_with(
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
            filters=filters,
            top=top,
        )

    def test_search_by_text_empty_validation(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test ValidationError for empty search text."""
        filters = []
        top = 10

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(ValidationError, match="Searched text cannot be empty"):
            service.search_by_text_and_filters_with_type(
                text="",
                filters=filters,
                top=top,
                search_type=SearchType.SEMANTIC,
            )

        with pytest.raises(ValidationError, match="Searched text cannot be empty"):
            service.search_by_text_and_filters_with_type(
                text="   ",
                filters=filters,
                top=top,
                search_type=SearchType.SEMANTIC,
            )

    def test_search_by_text_encoding_error(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EmbeddingError during search encoding."""
        text = "search text"
        filters = []
        top = 10

        mock_embedding_service.encode.side_effect = Exception("Encoding failed")

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(EmbeddingError, match="Dense encoding error"):
            service.search_by_text_and_filters_with_type(
                text=text,
                filters=filters,
                top=top,
                search_type=SearchType.SEMANTIC,
            )

    def test_search_by_text_unsupported_type(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test ValidationError for unsupported search type."""
        text = "search text"
        filters = []
        top = 10

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        # Test with an invalid search type (we'll mock it)
        with pytest.raises(ValidationError, match="Unsupported search type"):
            service.search_by_text_and_filters_with_type(
                text=text,
                filters=filters,
                top=top,
                search_type="INVALID_TYPE",  # This will cause the validation error
            )

    def test_search_by_text_sparse_encoding_error(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EmbeddingError during sparse search encoding."""
        text = "search text"
        filters = []
        top = 10

        mock_sparse_embedding_service.encode.side_effect = Exception(
            "Sparse encoding failed",
        )

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        with pytest.raises(EmbeddingError, match="Sparse encoding error"):
            service.search_by_text_and_filters_with_type(
                text=text,
                filters=filters,
                top=top,
                search_type=SearchType.SPARSE,
            )

    def test_search_by_text_hybrid_encoding_error(
        self,
        mock_repository: RepositoryContract,
        mock_embedding_service: EmbeddingServiceContract,
        mock_sparse_embedding_service: SparseEmbeddingServiceContract,
    ) -> None:
        """Test EmbeddingError during hybrid search encoding."""
        text = "search text"
        filters = []
        top = 10

        service = EntityService(
            mock_repository,
            mock_embedding_service,
            mock_sparse_embedding_service,
        )

        service.sparse_embedding_service.encode.side_effect = Exception(
            "Sparse encoding failed",
        )
        with pytest.raises(EmbeddingError, match="Encoding error"):
            service.search_by_text_and_filters_with_type(
                text=text,
                filters=filters,
                top=top,
                search_type=SearchType.HYBRID,
            )

        service.dense_embedding_service.encode.side_effect = Exception(
            "Dense encoding failed",
        )
        with pytest.raises(EmbeddingError, match="Encoding error"):
            service.search_by_text_and_filters_with_type(
                text=text,
                filters=filters,
                top=top,
                search_type=SearchType.HYBRID,
            )
