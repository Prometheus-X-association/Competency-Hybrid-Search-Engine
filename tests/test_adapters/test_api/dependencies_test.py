"""Test module for API dependencies."""

import pytest
from fastapi import Request
from logger import LoggerContract
from pytest_mock import MockerFixture
from sentence_transformers import SentenceTransformer, SparseEncoder
from starlette.datastructures import State

from adapters.api.dependencies import (
    get_config,
    get_db_client,
    get_dense_embedding_service,
    get_embedding_model,
    get_entity_service,
    get_logger,
    get_repository,
    get_sparse_embedding_model,
    get_sparse_embedding_service,
)
from adapters.infrastructure.config.contract import ConfigContract
from domain.contracts.db_client import ClientWrapperContract
from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.contracts.repository import RepositoryContract
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.services.entity_service import EntityService


class TestAPIDependencies:
    """Test class for API dependencies."""

    @pytest.fixture
    def mock_embedding_model(self, mocker: MockerFixture) -> SentenceTransformer:
        """Create mock embedding model."""
        return mocker.Mock(spec=SentenceTransformer)

    @pytest.fixture
    def mock_sparse_model(self, mocker: MockerFixture) -> SparseEncoder:
        """Create mock sparse embedding model."""
        return mocker.Mock(spec=SparseEncoder)

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> ClientWrapperContract:
        """Create mock database client."""
        return mocker.Mock(spec=ClientWrapperContract)

    @pytest.fixture
    def mock_request(
        self,
        mock_embedding_model: SentenceTransformer,
        mock_sparse_model: SparseEncoder,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> Request:
        """Create mock request with state."""
        request = mocker.Mock(spec=Request)
        request.state = mocker.Mock(spec=State)
        request.state.config = mock_config
        request.state.logger = mock_logger
        request.state.model = mock_embedding_model
        request.state.sparse_model = mock_sparse_model
        return request

    @pytest.mark.asyncio
    async def test_get_config(self, mock_request: Request) -> None:
        """Test get_config dependency."""
        result = await get_config(mock_request)
        assert result == mock_request.state.config

    @pytest.mark.asyncio
    async def test_get_logger(self, mock_request: Request) -> None:
        """Test get_logger dependency."""
        result = await get_logger(mock_request)
        assert result == mock_request.state.logger

    @pytest.mark.asyncio
    async def test_get_embedding_model(self, mock_request: Request) -> None:
        """Test get_embedding_model dependency."""
        result = await get_embedding_model(mock_request)
        assert result == mock_request.state.model

    @pytest.mark.asyncio
    async def test_get_sparse_embedding_model(self, mock_request: Request) -> None:
        """Test get_sparse_embedding_model dependency."""
        result = await get_sparse_embedding_model(mock_request)
        assert result == mock_request.state.sparse_model

    @pytest.mark.asyncio
    async def test_get_db_client(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test get_db_client dependency (cleaner, less brittle)."""
        # Patch QdrantClientWrapper to simply return a mock instance
        mock_wrapper_instance = mocker.Mock(spec=ClientWrapperContract)
        patched_wrapper = mocker.patch(
            "adapters.api.dependencies.QdrantClientWrapper",
            return_value=mock_wrapper_instance,
        )

        result = await get_db_client(mock_config, mock_logger)

        assert result is mock_wrapper_instance
        patched_wrapper.assert_called_once_with(
            url="http://localhost:6333",
            api_key="test_api_key",
            logger=mock_logger,
        )

    @pytest.mark.asyncio
    async def test_get_repository(
        self,
        mock_client: ClientWrapperContract,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test get_repository dependency."""
        mock_repo_instance = mocker.Mock(spec=RepositoryContract)
        patched_repo = mocker.patch(
            "adapters.api.dependencies.QdrantRepository",
            return_value=mock_repo_instance,
        )

        result = await get_repository(mock_client, mock_config, mock_logger)

        assert result == mock_repo_instance
        patched_repo.assert_called_once_with(
            client=mock_client.get_client(),
            collection_name="test_collection",
            logger=mock_logger,
            dense_vector_name="dense",
            sparse_vector_name="sparse",
        )

    @pytest.mark.asyncio
    async def test_get_dense_embedding_service(
        self,
        mock_embedding_model: SentenceTransformer,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test get_dense_embedding_service dependency."""
        mock_service_instance = mocker.Mock(spec=EmbeddingServiceContract)
        patched_service = mocker.patch(
            "adapters.api.dependencies.HuggingfaceEmbeddingService",
            return_value=mock_service_instance,
        )

        result = await get_dense_embedding_service(mock_embedding_model, mock_logger)

        assert result == mock_service_instance
        patched_service.assert_called_once_with(
            logger=mock_logger,
            model=mock_embedding_model,
        )

    @pytest.mark.asyncio
    async def test_get_sparse_embedding_service(
        self,
        mock_sparse_model: SparseEncoder,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test get_sparse_embedding_service dependency."""
        mock_service_instance = mocker.Mock(spec=SparseEmbeddingServiceContract)
        patched_service = mocker.patch(
            "adapters.api.dependencies.HuggingfaceSparseEmbeddingService",
            return_value=mock_service_instance,
        )

        result = await get_sparse_embedding_service(mock_sparse_model, mock_logger)

        assert result == mock_service_instance
        patched_service.assert_called_once_with(
            logger=mock_logger,
            model=mock_sparse_model,
        )

    @pytest.mark.asyncio
    async def test_get_entity_service(
        self,
        mock_repository: RepositoryContract,
        mocker: MockerFixture,
    ) -> None:
        """Test get_entity_service dependency."""
        mock_entity_service_instance = mocker.Mock(spec=EntityService)
        patched_entity_service = mocker.patch(
            "adapters.api.dependencies.EntityService",
            return_value=mock_entity_service_instance,
        )

        dense_service = mocker.Mock(spec=EmbeddingServiceContract)
        sparse_service = mocker.Mock(spec=SparseEmbeddingServiceContract)

        result = await get_entity_service(
            mock_repository,
            dense_service,
            sparse_service,
        )

        assert result == mock_entity_service_instance
        patched_entity_service.assert_called_once_with(
            repository=mock_repository,
            dense_embedding_service=dense_service,
            sparse_embedding_service=sparse_service,
        )

    @pytest.mark.asyncio
    async def test_dependencies_chain_integration(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
        mock_embedding_model: SentenceTransformer,
        mock_sparse_model: SparseEncoder,
        mocker: MockerFixture,
    ) -> None:
        """Test that dependencies work together in chain."""
        mock_qdrant_wrapper = mocker.Mock(spec=ClientWrapperContract)
        mocker.patch(
            "adapters.api.dependencies.QdrantClientWrapper",
            return_value=mock_qdrant_wrapper,
        )

        mock_qdrant_repo = mocker.Mock(spec=RepositoryContract)
        mocker.patch(
            "adapters.api.dependencies.QdrantRepository",
            return_value=mock_qdrant_repo,
        )

        mock_dense_service = mocker.Mock(spec=EmbeddingServiceContract)
        mocker.patch(
            "adapters.api.dependencies.HuggingfaceEmbeddingService",
            return_value=mock_dense_service,
        )

        mock_sparse_service = mocker.Mock(spec=SparseEmbeddingServiceContract)
        mocker.patch(
            "adapters.api.dependencies.HuggingfaceSparseEmbeddingService",
            return_value=mock_sparse_service,
        )

        mock_entity_service = mocker.Mock(spec=EntityService)
        mocker.patch(
            "adapters.api.dependencies.EntityService",
            return_value=mock_entity_service,
        )

        mock_qdrant_wrapper.get_client.return_value = mocker.Mock(
            spec=ClientWrapperContract,
        )

        # Test dependency chain
        db_client = await get_db_client(mock_config, mock_logger)
        repository = await get_repository(db_client, mock_config, mock_logger)
        dense_service = await get_dense_embedding_service(
            mock_embedding_model,
            mock_logger,
        )
        sparse_service = await get_sparse_embedding_service(
            mock_sparse_model,
            mock_logger,
        )
        entity_service = await get_entity_service(
            repository,
            dense_service,
            sparse_service,
        )

        assert db_client == mock_qdrant_wrapper
        assert repository == mock_qdrant_repo
        assert dense_service == mock_dense_service
        assert sparse_service == mock_sparse_service
        assert entity_service == mock_entity_service
