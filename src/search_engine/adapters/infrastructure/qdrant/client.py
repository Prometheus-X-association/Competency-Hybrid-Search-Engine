from typing import override

from logger import LoggerContract
from qdrant_client import QdrantClient
from qdrant_client.models import SparseVectorParams, VectorParams

from adapters.exceptions import CollectionCreationError, DBConnectionError
from domain.contracts.db_client import ClientWrapperContract


class QdrantClientWrapper(ClientWrapperContract[QdrantClient]):
    """Wrapper for QdrantClient to manage connection and logging."""

    def __init__(self, url: str, api_key: str | None, logger: LoggerContract) -> None:
        """Initialize the QdrantClientWrapper.

        Args:
            url (str): The URL of the Qdrant instance (e.g., http://localhost:6333).
            api_key (str | None): The API key for Qdrant, if required.
            logger (LoggerContract): The logger instance for logging.
        """
        self.url = url
        self.api_key = api_key
        self.logger = logger

        self.client = self._connect_to_qdrant()

    def _connect_to_qdrant(self) -> QdrantClient:
        """Establishes connection to the Qdrant database.

        Returns:
            QdrantClient: The connected Qdrant client instance.

        Raises:
            DBConnectionError: If connection to Qdrant fails.
        """
        log_context = {"url": self.url}
        try:
            client = QdrantClient(url=self.url, api_key=self.api_key)
            self.logger.debug("QdrantClient connected.", context=log_context)
        except Exception as e:
            self.logger.exception(
                "Failed to connect to Qdrant",
                context=log_context,
                exc=e,
            )
            raise DBConnectionError(
                f"Failed to connect to Qdrant at '{self.url}'",
            ) from e
        else:
            return client

    @override
    def create_db_collection_if_not_exists(
        self,
        collection_name: str,
        vector_dimensions: int,
        vector_distance: str,
        dense_vector_name: str,
        sparse_vector_name: str,
    ) -> None:
        """Checks if a collection exists in the database and creates it if not.

        Args:
            collection_name (str): The name of the collection to check or create.
            vector_dimensions (int): The dimensions of the vectors in the collection.
            vector_distance (str): The distance metric for the vectors.
            dense_vector_name (str): Name for dense vector.
            sparse_vector_name (str): Name for sparse vector.

        Raises:
            CollectionCreationError: If there is an error
                checking or creating the collection.
        """
        log_context = {"collection_name": collection_name}
        self.logger.debug(
            "Checking if the collection already exists",
            context=log_context,
        )

        # Check if the collection already exists
        try:
            if collection_name in {
                col.name for col in self.client.get_collections().collections
            }:
                self.logger.debug(
                    "Collection already exists",
                    context=log_context,
                )
                return
        except Exception as e:
            self.logger.exception(
                "Error checking collection",
                context=log_context,
                exc=e,
            )
            raise CollectionCreationError(
                f"Error checking collection '{collection_name}'",
            ) from e

        self.logger.debug(
            "Creating collection",
            context=log_context,
        )

        # Creation of the collection
        try:
            response = self.client.create_collection(
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
        except Exception as e:
            self.logger.exception(
                "Error creating collection",
                context=log_context,
                exc=e,
            )
            raise CollectionCreationError(
                f"Error creating collection '{collection_name}'",
            ) from e

        if response is not True:
            self.logger.error(
                "Failed to create collection",
                context=log_context,
            )
            raise CollectionCreationError(
                f"Failed to create collection '{collection_name}'",
            )

        self.logger.debug(
            "Collection created successfully in Qdrant",
            context=log_context,
        )

        return

    @override
    def get_client(self) -> QdrantClient:
        """Gets the Qdrant client instance.

        Returns:
            QdrantClient: The Qdrant client instance.
        """
        return self.client
