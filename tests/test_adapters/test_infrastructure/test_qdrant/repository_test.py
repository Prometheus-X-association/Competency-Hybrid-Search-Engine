"""Test module for Qdrant repository implementation."""

from uuid import UUID

import pytest
from logger import LoggerContract
from pydantic import ValidationError as PydanticValidationError
from pytest_mock import MockerFixture
from qdrant_client import QdrantClient
from qdrant_client.models import (
    NamedSparseVector,
    NamedVector,
    QueryResponse,
    ScoredPoint,
    UpdateResult,
)
from qdrant_client.models import (
    SparseVector as QdrantSparseVector,
)

from adapters.exceptions import RepositoryError
from adapters.infrastructure.qdrant.repository import QdrantRepository
from domain.exceptions import ValidationError
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.filters import DomainFilter, DomainFilterOperator
from domain.types.identifier import Identifier
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import DenseVector, SparseVector, VectorName


class TestQdrantRepository:
    """Test class for QdrantRepository."""

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> QdrantClient:
        """Create mock Qdrant client."""
        return mocker.Mock(spec=QdrantClient)

    @pytest.fixture
    def repository(
        self,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
    ) -> QdrantRepository:
        """Create QdrantRepository instance."""
        return QdrantRepository(
            client=mock_client,
            collection_name="test-collection",
            logger=mock_logger,
            dense_vector_name="dense",
            sparse_vector_name="sparse",
        )

    @pytest.fixture
    def create_entity_model(
        self,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> CreateEntityModel:
        """Create CreateEntityModel."""
        return CreateEntityModel(
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

    @pytest.fixture
    def update_entity_model(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> UpdateEntityModel:
        """Create UpdateEntityModel."""
        return UpdateEntityModel(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

    @pytest.fixture
    def returned_scored_point(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> ScoredPoint:
        """Create a ScoredPoint as returned from Qdrant."""
        return ScoredPoint(
            id=str(sample_identifier),
            payload=sample_competency.model_dump(),
            score=0.95,
            version=1,
        )

    def test_init(
        self,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
    ) -> None:
        """Test repository initialization."""
        repo = QdrantRepository(
            client=mock_client,
            collection_name="test-collection",
            logger=mock_logger,
            dense_vector_name="dense",
            sparse_vector_name="sparse",
        )

        assert repo.client == mock_client
        assert repo.collection_name == "test-collection"
        assert repo.logger == mock_logger
        assert repo.dense_vector_name == "dense"
        assert repo.sparse_vector_name == "sparse"

    # Create
    def test_create_entity_success(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        create_entity_model: CreateEntityModel,
        mocker: MockerFixture,
    ) -> None:
        """Test successful entity creation."""
        # Mock successful response
        mock_response = mocker.Mock(spec=UpdateResult)
        mock_response.status = "completed"
        mock_client.upsert.return_value = mock_response

        result = repository.create_entity(create_entity_model)

        assert isinstance(result, Entity)
        assert isinstance(result.identifier, UUID)
        assert result.competency == create_entity_model.competency

        # Verify client was called
        mock_client.upsert.assert_called_once_with(
            collection_name="test-collection",
            points=mocker.ANY,
        )

        # Verify logging
        mock_logger.info.assert_called_once_with(
            "Entity created",
            context={"id": result.identifier},
        )

    def test_create_entity_client_error(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        create_entity_model: CreateEntityModel,
    ) -> None:
        """Test entity creation with client error."""
        mock_client.upsert.side_effect = Exception("Client error")

        with pytest.raises(RepositoryError) as exc_info:
            repository.create_entity(create_entity_model)

        assert "Failed to create entity" in str(exc_info.value)
        mock_logger.exception.assert_called_once()

    def test_create_entity_invalid_status(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        create_entity_model: CreateEntityModel,
        mocker: MockerFixture,
    ) -> None:
        """Test entity creation with invalid status response."""
        mock_response = mocker.Mock(spec=UpdateResult)
        mock_response.status = "failed"
        mock_client.upsert.return_value = mock_response

        with pytest.raises(RepositoryError) as exc_info:
            repository.create_entity(create_entity_model)

        assert "invalid response status" in str(exc_info.value)
        mock_logger.error.assert_called_once()

    # Get
    def test_get_entity_success(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_competency: Competency,
        sample_identifier: Identifier,
        mocker: MockerFixture,
    ) -> None:
        """Test successful entity retrieval."""
        entity_id = sample_identifier

        # Mock point data
        mock_point = mocker.Mock(spec=object)
        mock_point.payload = sample_competency.model_dump()
        mock_point.vector = {
            "dense": [0.1, 0.2, 0.3],
            "sparse": {"indices": [0, 1, 2], "values": [0.8, 0.6, 0.4]},
        }

        mock_client.retrieve.return_value = [mock_point]

        result = repository.get_entity(entity_id)

        assert isinstance(result, Entity)
        assert result.identifier == entity_id
        assert result.competency.title == sample_competency.title
        assert result.dense_vector.values == [0.1, 0.2, 0.3]
        assert result.sparse_vector.indices == [0, 1, 2]

        mock_client.retrieve.assert_called_once_with(
            collection_name="test-collection",
            ids=[str(entity_id)],
            with_payload=True,
            with_vectors=True,
        )

    def test_get_entity_success_qdrant_sparse_vector(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_competency: Competency,
        sample_identifier: Identifier,
        mocker: MockerFixture,
    ) -> None:
        """Test successful entity retrieval."""
        entity_id = sample_identifier

        # Mock point data
        mock_point = mocker.Mock(spec=object)
        mock_point.payload = sample_competency.model_dump()
        mock_point.vector = {
            "dense": [0.1, 0.2, 0.3],
            "sparse": QdrantSparseVector(indices=[0, 1, 2], values=[0.8, 0.6, 0.4]),
        }

        mock_client.retrieve.return_value = [mock_point]

        result = repository.get_entity(entity_id)

        assert isinstance(result, Entity)
        assert result.identifier == entity_id
        assert result.competency.title == sample_competency.title
        assert result.dense_vector.values == [0.1, 0.2, 0.3]
        assert result.sparse_vector.indices == [0, 1, 2]

        mock_client.retrieve.assert_called_once_with(
            collection_name="test-collection",
            ids=[str(entity_id)],
            with_payload=True,
            with_vectors=True,
        )

    def test_get_entity_not_found(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        sample_identifier: Identifier,
    ) -> None:
        """Test entity retrieval when entity not found."""
        entity_id = sample_identifier
        mock_client.retrieve.return_value = []

        result = repository.get_entity(entity_id)

        assert result is None
        mock_logger.info.assert_called_with(
            "Entity not found",
            context={"id": entity_id},
        )

    def test_get_entity_client_error(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        sample_identifier: Identifier,
    ) -> None:
        """Test entity retrieval with client error."""
        entity_id = sample_identifier
        mock_client.retrieve.side_effect = Exception("Retrieve error")

        with pytest.raises(RepositoryError) as exc_info:
            repository.get_entity(entity_id)

        assert "Failed to get entity" in str(exc_info.value)
        mock_logger.exception.assert_called_once()

    # Update
    def test_update_entity_success(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        update_entity_model: UpdateEntityModel,
    ) -> None:
        """Test successful entity update."""
        result = repository.update_entity(update_entity_model)

        assert isinstance(result, Entity)
        assert result.identifier == update_entity_model.identifier
        assert result.competency == update_entity_model.competency

        mock_client.upsert.assert_called_once()
        mock_logger.info.assert_called_with(
            "Entity updated successfully",
            context={"id": update_entity_model.identifier},
        )

    def test_update_entity_client_error(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        update_entity_model: UpdateEntityModel,
    ) -> None:
        """Test entity update with client error."""
        mock_client.upsert.side_effect = Exception("Update error")

        with pytest.raises(RepositoryError) as exc_info:
            repository.update_entity(update_entity_model)

        assert "Failed to update entity" in str(exc_info.value)
        mock_logger.exception.assert_called_once()

    # Delete
    def test_delete_entity_success(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        sample_identifier: Identifier,
    ) -> None:
        """Test successful entity deletion."""
        entity_id = sample_identifier

        repository.delete_entity(entity_id)

        mock_client.delete.assert_called_once_with(
            collection_name="test-collection",
            points_selector=[str(entity_id)],
        )
        mock_logger.info.assert_called_with(
            "Entity deleted successfully",
            context={"id": entity_id},
        )

    def test_delete_entity_client_error(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        sample_identifier: Identifier,
    ) -> None:
        """Test entity deletion with client error."""
        entity_id = sample_identifier
        mock_client.delete.side_effect = Exception("Delete error")

        with pytest.raises(RepositoryError) as exc_info:
            repository.delete_entity(entity_id)

        assert "Failed to delete entity" in str(exc_info.value)
        mock_logger.exception.assert_called_once()

    # Search by vector
    def test_search_by_vector_dense(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_dense_vector: DenseVector,
        returned_scored_point: ScoredPoint,
    ) -> None:
        """Test search by dense vector."""
        mocked_returned_items = [returned_scored_point]
        mock_client.search.return_value = mocked_returned_items

        for vector_name in [VectorName.DENSE, "dense"]:
            results = repository.search_by_vector_and_filters(
                vector=sample_dense_vector,
                filters=[],
                top=10,
                vector_name=vector_name,
            )

            assert len(results) == len(mocked_returned_items)

            for result in results:
                assert isinstance(result, SearchResult)
                assert result.entity.identifier == Identifier(returned_scored_point.id)
                assert (
                    result.entity.competency.model_dump()
                    == returned_scored_point.payload
                )
                assert result.score == returned_scored_point.score

        assert mock_client.search.call_count == 2

        for call_args in mock_client.search.call_args_list:
            query_vector = call_args.kwargs.get("query_vector")
            assert isinstance(query_vector, NamedVector)

    def test_search_by_vector_sparse(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_sparse_vector: SparseVector,
        returned_scored_point: ScoredPoint,
    ) -> None:
        """Test search by sparse vector."""
        mocked_returned_items = [returned_scored_point]
        mock_client.search.return_value = mocked_returned_items

        for vector_name in [VectorName.SPARSE, "sparse"]:
            results = repository.search_by_vector_and_filters(
                vector=sample_sparse_vector,
                filters=[],
                top=10,
                vector_name=vector_name,
            )

            assert len(results) == len(mocked_returned_items)

            for result in results:
                assert isinstance(result, SearchResult)
                assert result.entity.identifier == Identifier(returned_scored_point.id)
                assert (
                    result.entity.competency.model_dump()
                    == returned_scored_point.payload
                )
                assert result.score == returned_scored_point.score

        assert mock_client.search.call_count == 2

        for call_args in mock_client.search.call_args_list:
            query_vector = call_args.kwargs.get("query_vector")
            assert isinstance(query_vector, NamedSparseVector)

    def test_search_by_vector_unsupported_type(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
    ) -> None:
        """Test search with unsupported vector type."""
        with pytest.raises(RepositoryError) as exc_info:
            repository.search_by_vector_and_filters(
                vector=sample_dense_vector,
                filters=[],
                top=10,
                vector_name="unsupported",
            )

        assert "Unsupported vector type" in str(exc_info.value)
        mock_client.search.assert_not_called()

    def test_search_by_vector_with_filters(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_dense_vector: DenseVector,
        returned_scored_point: ScoredPoint,
    ) -> None:
        """Test search with filters."""
        mocked_returned_items = [returned_scored_point]
        mock_client.search.return_value = mocked_returned_items

        filters = [
            DomainFilter(
                field="type",
                value="TECHNICAL",
                operator=DomainFilterOperator.EQUAL,
            ),
            DomainFilter(
                field="type",
                value="NOT TECHNICAL",
                operator=DomainFilterOperator.NOT_EQUAL,
            ),
        ]

        result = repository.search_by_vector_and_filters(
            vector=sample_dense_vector,
            filters=filters,
            top=10,
            vector_name=VectorName.DENSE,
        )

        assert len(result) == 1
        mock_client.search.assert_called_once()

        for call_args in mock_client.search.call_args_list:
            filter_used = call_args.kwargs.get("query_filter")
            assert isinstance(filter_used.must, list)
            assert len(filter_used.must) == 1
            assert isinstance(filter_used.must_not, list)
            assert len(filter_used.must_not) == 1

    def test_search_by_vector_pydantic_validation_error(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
        mocker: MockerFixture,
    ) -> None:
        """Test PydanticValidationError during filter building."""
        # Create a filter that will cause a PydanticValidationError
        filters = [
            DomainFilter(
                field="test",
                value="test",
                operator=DomainFilterOperator.EQUAL,
            ),
        ]

        mocker.patch.object(
            repository,
            "_build_search_filters",
            side_effect=PydanticValidationError("Invalid filter", []),
        )

        with pytest.raises(ValidationError, match="Invalid filters"):
            repository.search_by_vector_and_filters(
                vector=sample_dense_vector,
                filters=filters,
                top=10,
                vector_name=VectorName.DENSE,
            )

        mock_client.search.assert_not_called()

    def test_search_by_vector_filter_building_error(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
        mocker: MockerFixture,
    ) -> None:
        """Test Exception during filter building in search_by_vector_and_filters."""
        filters = [
            DomainFilter(
                field="test",
                value="test",
                operator=DomainFilterOperator.EQUAL,
            ),
        ]

        # Mock _build_search_filters to raise Exception
        mocker.patch.object(
            repository,
            "_build_search_filters",
            side_effect=Exception("Filter error"),
        )

        with pytest.raises(RepositoryError, match="Failed to build search filters"):
            repository.search_by_vector_and_filters(
                vector=sample_dense_vector,
                filters=filters,
                top=10,
                vector_name=VectorName.DENSE,
            )

        mock_client.search.assert_not_called()

    def test_search_by_vector_client_search_error(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test Exception during client.search in search_by_vector_and_filters."""
        # Mock client.search to raise Exception
        mock_client.search.side_effect = Exception("Search operation failed")

        # Test with dense vector
        with pytest.raises(RepositoryError, match="Failed search_by_vector"):
            repository.search_by_vector_and_filters(
                vector=sample_dense_vector,
                filters=[],
                top=10,
                vector_name=VectorName.DENSE,
            )

        # Test with sparse vector to cover both vector info logging branches
        with pytest.raises(RepositoryError, match="Failed search_by_vector"):
            repository.search_by_vector_and_filters(
                vector=sample_sparse_vector,
                filters=[],
                top=10,
                vector_name=VectorName.SPARSE,
            )

    # Search Hybrid
    def test_search_hybrid_success(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
        returned_scored_point: ScoredPoint,
        mocker: MockerFixture,
    ) -> None:
        """Test successful hybrid search."""
        mock_response = mocker.Mock(spec=QueryResponse)
        mock_response.points = [returned_scored_point]
        mock_client.query_points.return_value = mock_response

        result = repository.search_hybrid_by_vectors_and_filters(
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
            filters=[],
            top=10,
        )

        assert len(result) == 1
        assert isinstance(result[0], SearchResult)
        assert result[0].entity.identifier == Identifier(returned_scored_point.id)
        assert result[0].score == returned_scored_point.score

        mock_client.query_points.assert_called_once()

    def test_search_hybrid_client_error(
        self,
        repository: QdrantRepository,
        mock_client: QdrantClient,
        mock_logger: LoggerContract,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test hybrid search with client error."""
        mock_client.query_points.side_effect = Exception("Hybrid search error")

        with pytest.raises(RepositoryError) as exc_info:
            repository.search_hybrid_by_vectors_and_filters(
                dense_vector=sample_dense_vector,
                sparse_vector=sample_sparse_vector,
                filters=[],
                top=10,
            )

        assert "Failed hybrid search" in str(exc_info.value)
        mock_logger.exception.assert_called_once()

    def test_search_hybrid_pydantic_validation_error(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
        mocker: MockerFixture,
    ) -> None:
        """Test PydanticValidationError during filter building."""
        filters = [
            DomainFilter(
                field="test",
                value="test",
                operator=DomainFilterOperator.EQUAL,
            ),
        ]

        mocker.patch.object(
            repository,
            "_build_search_filters",
            side_effect=PydanticValidationError("Invalid filter", []),
        )

        with pytest.raises(ValidationError, match="Invalid filters"):
            repository.search_hybrid_by_vectors_and_filters(
                dense_vector=sample_dense_vector,
                sparse_vector=sample_sparse_vector,
                filters=filters,
                top=10,
            )

        mock_client.query_points.assert_not_called()

    def test_search_hybrid_filter_building_error(
        self,
        mock_client: QdrantClient,
        repository: QdrantRepository,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
        mocker: MockerFixture,
    ) -> None:
        """Test Exception during filter building."""
        filters = [
            DomainFilter(
                field="test",
                value="test",
                operator=DomainFilterOperator.EQUAL,
            ),
        ]

        # Mock _build_search_filters to raise Exception
        mocker.patch.object(
            repository,
            "_build_search_filters",
            side_effect=Exception("Filter error"),
        )

        with pytest.raises(RepositoryError, match="Failed to build search filters"):
            repository.search_hybrid_by_vectors_and_filters(
                dense_vector=sample_dense_vector,
                sparse_vector=sample_sparse_vector,
                filters=filters,
                top=10,
            )

        mock_client.query_points.assert_not_called()

    # Build Search
    def test_build_search_filters_empty(self, repository: QdrantRepository) -> None:
        """Test building search filters with empty list."""
        result = repository._build_search_filters([])

        # Should return empty Filter
        assert result.must is None
        assert result.must_not is None

    def test_build_search_filters_equal_operator(
        self,
        repository: QdrantRepository,
    ) -> None:
        """Test building search filters with equal operator."""
        filters = [
            DomainFilter(
                field="type",
                value="TECHNICAL",
                operator=DomainFilterOperator.EQUAL,
            ),
        ]

        result = repository._build_search_filters(filters)

        assert result.must is not None
        assert len(result.must) == 1
        assert result.must_not is None

    def test_build_search_filters_not_equal_operator(
        self,
        repository: QdrantRepository,
    ) -> None:
        """Test building search filters with not equal operator."""
        filters = [
            DomainFilter(
                field="type",
                value="SOFT",
                operator=DomainFilterOperator.NOT_EQUAL,
            ),
        ]

        result = repository._build_search_filters(filters)

        assert result.must is None
        assert result.must_not is not None
        assert len(result.must_not) == 1

    def test_build_search_filters_multiple_operators(
        self,
        repository: QdrantRepository,
    ) -> None:
        """Test building search filters with multiple operators."""
        filters = [
            DomainFilter(
                field="type",
                value="TECHNICAL",
                operator=DomainFilterOperator.EQUAL,
            ),
            DomainFilter(
                field="level",
                value="BEGINNER",
                operator=DomainFilterOperator.NOT_EQUAL,
            ),
            DomainFilter(
                field="category",
                value=["PROGRAMMING", "DATA"],
                operator=DomainFilterOperator.IN,
            ),
        ]

        result = repository._build_search_filters(filters)

        assert result.must is not None
        assert len(result.must) == 2  # EQUAL and IN
        assert result.must_not is not None
        assert len(result.must_not) == 1  # NOT_EQUAL

    # Create Field Condition
    def test_create_field_condition_equal(self) -> None:
        """Test creating field condition with equal operator."""
        domain_filter = DomainFilter(
            field="type",
            value="TECHNICAL",
            operator=DomainFilterOperator.EQUAL,
        )

        result = QdrantRepository._create_field_condition(domain_filter)

        assert result.key == "type"
        assert result.match.value == "TECHNICAL"

    def test_create_field_condition_not_equal(self) -> None:
        """Test creating field condition with not equal operator."""
        domain_filter = DomainFilter(
            field="type",
            value="TECHNICAL",
            operator=DomainFilterOperator.NOT_EQUAL,
        )

        result = QdrantRepository._create_field_condition(domain_filter)

        assert result.key == "type"
        assert result.match.value == "TECHNICAL"

    def test_create_field_condition_in(self) -> None:
        """Test creating field condition with in operator."""
        domain_filter = DomainFilter(
            field="category",
            value=["PROGRAMMING", "DATA"],
            operator=DomainFilterOperator.IN,
        )

        result = QdrantRepository._create_field_condition(domain_filter)

        assert result.key == "category"
        assert result.match.any == ["PROGRAMMING", "DATA"]

    def test_create_field_condition_not_in(self) -> None:
        """Test creating field condition with not in operator."""
        domain_filter = DomainFilter(
            field="category",
            value=["PROGRAMMING", "DATA"],
            operator=DomainFilterOperator.NOT_IN,
        )

        result = QdrantRepository._create_field_condition(domain_filter)

        assert result.key == "category"
        assert result.match.any == ["PROGRAMMING", "DATA"]

    def test_create_field_condition_range_operators(self) -> None:
        """Test creating field conditions with range operators."""
        test_cases = [
            (DomainFilterOperator.GREATER_THAN, "gt"),
            (DomainFilterOperator.GREATER_THAN_OR_EQUAL, "gte"),
            (DomainFilterOperator.LESS_THAN, "lt"),
            (DomainFilterOperator.LESS_THAN_OR_EQUAL, "lte"),
        ]

        for operator, expected_attr in test_cases:
            domain_filter = DomainFilter(field="score", value=0.5, operator=operator)

            result = QdrantRepository._create_field_condition(domain_filter)

            assert result.key == "score"
            assert hasattr(result.range, expected_attr)
            assert getattr(result.range, expected_attr) == 0.5
