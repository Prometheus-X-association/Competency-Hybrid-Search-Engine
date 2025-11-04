from abc import abstractmethod

from configcore import ConfigContract as CoreConfigContract


class ConfigContract(CoreConfigContract):
    """Contract for application configuration including db and embedding settings."""

    @abstractmethod
    def get_db_method(self) -> str:
        """Database method to use.

        Returns:
            str: The database method (e.g., 'qdrant').
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_host(self) -> str:
        """Qdrant database host.

        Returns:
            str: The host of the Qdrant instance.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_port(self) -> int:
        """Database port.

        Returns:
            int: The port of the database instance.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_url(self) -> str:
        """URL of the database instance.

        Returns:
            str: The URL of the database instance.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_api_key(self) -> str | None:
        """API key for database authentication. If not set, the default is None.

        Returns:
            str | None: The API key for database authentication.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_collection(self) -> str:
        """Name of the database collection to use.

        Returns:
            str: The name of the database collection.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_vector_distance(self) -> str:
        """Distance metric for database vectors.

        Returns:
            str: The distance metric for database vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def get_db_vector_dimensions(self) -> int:
        """Number of dimensions for the database vectors.

        Returns:
            int: The number of dimensions for the database vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def get_dense_vector_name(self) -> str:
        """Name of the dense vector in the database.

        Returns:
            str: The name of the dense vector in the database.
        """
        raise NotImplementedError

    @abstractmethod
    def get_sparse_vector_name(self) -> str:
        """Name of the sparse vector in the database.

        Returns:
            str: The name of the sparse vector in the database.
        """
        raise NotImplementedError

    @abstractmethod
    def get_embedding_method(self) -> str:
        """Embedding method to use.

        Returns:
            str: The embedding method (e.g., 'hf' for HuggingFace).
        """
        raise NotImplementedError

    @abstractmethod
    def get_embedding_model_name(self) -> str:
        """Name or path of the embedding model to use for vectorization.

        Returns:
            str: The name or path of the embedding model.
        """
        raise NotImplementedError

    @abstractmethod
    def get_embedding_vector_dimensions(self) -> int:
        """Number of dimensions for the embedding vectors.

        Returns:
            int: The number of dimensions for the embedding vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def get_sparse_embedding_model_name(self) -> str:
        """Name or path of the sparse embedding model to use for sparse vectorization.

        Returns:
            str: The name or path of the sparse embedding model.
        """
        raise NotImplementedError
