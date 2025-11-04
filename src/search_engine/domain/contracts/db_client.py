from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ClientType = TypeVar("ClientType")


class ClientWrapperContract(ABC, Generic[ClientType]):
    """Contract for a db client wrapper."""

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def get_client(self) -> ClientType:
        """Gets the client instance.

        Returns:
            ClientType: The client instance.
        """
        raise NotImplementedError
