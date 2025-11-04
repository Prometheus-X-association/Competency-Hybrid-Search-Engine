"""Test module for Qdrant client wrapper."""

import pytest
from logger import LoggerContract
from pytest_mock import MockerFixture
from qdrant_client import QdrantClient
from qdrant_client.models import (
    CollectionInfo,
    CollectionsResponse,
    SparseVectorParams,
    VectorParams,
)

from adapters.exceptions import CollectionCreationError, DBConnectionError
from adapters.infrastructure.qdrant.client import QdrantClientWrapper


class TestQdrantClientWrapper:
    """Test class for QdrantClientWrapper."""

    @pytest.fixture
    def mock_qdrant_client(self, mocker: MockerFixture) -> QdrantClient:
        """Create mock QdrantClient."""
        return mocker.Mock(spec=QdrantClient)

    def test_init_successful_connection(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test successful initialization and connection."""
        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        assert wrapper.url == "http://localhost:6333"
        assert wrapper.api_key == "test-key"
        assert wrapper.logger == mock_logger
        assert wrapper.client == mock_qdrant_client

        mock_client_class.assert_called_once_with(
            url="http://localhost:6333",
            api_key="test-key",
        )

    def test_init_connection_failure(
        self,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test initialization with connection failure."""
        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.side_effect = Exception("Connection failed")

        with pytest.raises(DBConnectionError) as exc_info:
            QdrantClientWrapper(
                url="http://localhost:6333",
                api_key="test-key",
                logger=mock_logger,
            )

        assert "Failed to connect to Qdrant at 'http://localhost:6333'" in str(
            exc_info.value,
        )
        mock_logger.exception.assert_called_once()

    def test_init_without_api_key(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test initialization without API key."""
        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key=None,
            logger=mock_logger,
        )

        assert wrapper.api_key is None
        mock_client_class.assert_called_once_with(
            url="http://localhost:6333",
            api_key=None,
        )

    def test_get_client(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test get_client method."""
        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        result = wrapper.get_client()
        assert result == mock_qdrant_client

    def test_create_collection_already_exists(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test create_db_collection_if_not_exists when collection already exists."""
        # Mock collections response
        mock_collection = mocker.Mock(spec=CollectionInfo)
        mock_collection.name = "test-collection"

        mock_collections_response = mocker.Mock(spec=CollectionsResponse)
        mock_collections_response.collections = [mock_collection]

        mock_qdrant_client.get_collections.return_value = mock_collections_response

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        wrapper.create_db_collection_if_not_exists(
            collection_name="test-collection",
            vector_dimensions=768,
            vector_distance="Cosine",
            dense_vector_name="dense",
            sparse_vector_name="sparse",
        )

        mock_qdrant_client.get_collections.assert_called_once()
        mock_qdrant_client.create_collection.assert_not_called()

    def test_create_collection_new_collection(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test create_db_collection_if_not_exists when creating new collection."""
        # Mock collections response (empty)
        mock_collections_response = mocker.Mock(spec=CollectionsResponse)
        mock_collections_response.collections = []

        mock_qdrant_client.get_collections.return_value = mock_collections_response
        mock_qdrant_client.create_collection.return_value = True

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )
        collection_name = "new-collection"
        vector_dimensions = 768
        vector_distance = "Cosine"
        dense_vector_name = "dense"
        sparse_vector_name = "sparse"

        wrapper.create_db_collection_if_not_exists(
            collection_name=collection_name,
            vector_dimensions=vector_dimensions,
            vector_distance=vector_distance,
            dense_vector_name=dense_vector_name,
            sparse_vector_name=sparse_vector_name,
        )

        mock_qdrant_client.get_collections.assert_called_once()
        mock_qdrant_client.create_collection.assert_called_once_with(
            collection_name=collection_name,
            vectors_config={
                dense_vector_name: VectorParams(
                    size=vector_dimensions,
                    distance=vector_distance,
                ),
            },
            sparse_vectors_config={
                sparse_vector_name: SparseVectorParams(),
            },
        )

    def test_create_collection_check_error(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test create_db_collection_if_not_exists when checking collections fails."""
        mock_qdrant_client.get_collections.side_effect = Exception("Check failed")

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        with pytest.raises(CollectionCreationError) as exc_info:
            wrapper.create_db_collection_if_not_exists(
                collection_name="test-collection",
                vector_dimensions=768,
                vector_distance="Cosine",
                dense_vector_name="dense",
                sparse_vector_name="sparse",
            )

        assert "Error checking collection 'test-collection'" in str(exc_info.value)
        mock_logger.exception.assert_called()

    def test_create_collection_creation_error(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test create_db_collection_if_not_exists when collection creation fails."""
        # Mock collections response (empty)
        mock_collections_response = mocker.Mock(spec=CollectionsResponse)
        mock_collections_response.collections = []

        mock_qdrant_client.get_collections.return_value = mock_collections_response
        mock_qdrant_client.create_collection.side_effect = Exception("Creation failed")

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        with pytest.raises(CollectionCreationError) as exc_info:
            wrapper.create_db_collection_if_not_exists(
                collection_name="test-collection",
                vector_dimensions=768,
                vector_distance="Cosine",
                dense_vector_name="dense",
                sparse_vector_name="sparse",
            )

        assert "Error creating collection 'test-collection'" in str(exc_info.value)
        mock_logger.exception.assert_called()

    def test_create_collection_creation_false_response(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test create_db_collection_if_not_exists when creation returns False."""
        # Mock collections response (empty)
        mock_collections_response = mocker.Mock(spec=CollectionsResponse)
        mock_collections_response.collections = []

        mock_qdrant_client.get_collections.return_value = mock_collections_response
        mock_qdrant_client.create_collection.return_value = False

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        with pytest.raises(CollectionCreationError) as exc_info:
            wrapper.create_db_collection_if_not_exists(
                collection_name="test-collection",
                vector_dimensions=768,
                vector_distance="Cosine",
                dense_vector_name="dense",
                sparse_vector_name="sparse",
            )

        assert "Failed to create collection 'test-collection'" in str(
            exc_info.value,
        )
        mock_logger.error.assert_called()

    def test_create_collection_successful_creation(
        self,
        mock_logger: LoggerContract,
        mock_qdrant_client: QdrantClient,
        mocker: MockerFixture,
    ) -> None:
        """Test successful collection creation with all logging."""
        # Mock collections response (empty)
        mock_collections_response = mocker.Mock(spec=CollectionsResponse)
        mock_collections_response.collections = []

        mock_qdrant_client.get_collections.return_value = mock_collections_response
        mock_qdrant_client.create_collection.return_value = True

        mock_client_class = mocker.patch(
            "adapters.infrastructure.qdrant.client.QdrantClient",
        )
        mock_client_class.return_value = mock_qdrant_client

        wrapper = QdrantClientWrapper(
            url="http://localhost:6333",
            api_key="test-key",
            logger=mock_logger,
        )

        collection_name = "test-collection"
        vector_dimensions = 768
        vector_distance = "Cosine"
        dense_vector_name = "dense"
        sparse_vector_name = "sparse"

        wrapper.create_db_collection_if_not_exists(
            collection_name=collection_name,
            vector_dimensions=vector_dimensions,
            vector_distance=vector_distance,
            dense_vector_name=dense_vector_name,
            sparse_vector_name=sparse_vector_name,
        )

        mock_qdrant_client.get_collections.assert_called_once()
        mock_qdrant_client.create_collection.assert_called_once_with(
            collection_name=collection_name,
            vectors_config={
                dense_vector_name: VectorParams(
                    size=vector_dimensions,
                    distance=vector_distance,
                ),
            },
            sparse_vectors_config={
                sparse_vector_name: SparseVectorParams(),
            },
        )

        mock_logger.debug.assert_called_with(
            "Collection created successfully in Qdrant",
            context={"collection_name": "test-collection"},
        )
