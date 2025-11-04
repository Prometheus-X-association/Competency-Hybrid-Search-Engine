from typing import override

from configcore import Settings as CoreSettings
from pydantic import Field, model_validator

from adapters.infrastructure.config.contract import ConfigContract


class Settings(CoreSettings, ConfigContract):
    """Configuration settings for the application.

    It extends CoreSettings and implements ConfigContract.
    """

    # Database configuration
    db_method: str = Field(
        default="qdrant",
        description="Database method to use",
    )

    # Qdrant configuration
    db_qdrant_host: str = Field(
        default="qdrant",
        description="Qdrant database host",
    )
    db_qdrant_port: int = Field(
        default=6333,
        description="Qdrant database port",
    )
    db_qdrant_url: str = Field(
        default="http://qdrant:6333",
        description="URL of the Qdrant instance (e.g. http://localhost:6333)",
    )
    db_qdrant_api_key: str | None = Field(
        default=None,
        description="API key for Qdrant (if needed)",
    )
    db_qdrant_collection: str = Field(
        default="entities",
        description="Name of the Qdrant collection",
    )
    db_qdrant_vector_distance: str = Field(
        default="Cosine",
        description=(
            "Distance metric for Qdrant vectors"
            "(Dot, Cosine, Euclid or Manhattan)."
            "Only useful if the collection doesn't exist."
        ),
    )
    db_qdrant_vector_dimensions: int = Field(
        default=1024,
        description=(
            "Number of dimensions for the Qdrant vectors. "
            "Only useful if the collection doesn't exist."
        ),
    )

    # Vector name configuration
    db_qdrant_dense_vector_name: str = Field(
        default="dense",
        min_length=1,
        description="Name of the dense vector in Qdrant collection",
    )
    db_qdrant_sparse_vector_name: str = Field(
        default="sparse",
        min_length=1,
        description="Name of the sparse vector in Qdrant collection",
    )

    # Embedding configuration
    embedding_method: str = Field(
        default="hf",
        description="Embedding method to use",
    )
    embedding_hf_model_name: str = Field(
        default="Qwen/Qwen3-Embedding-0.6B",
        description="Name or path of the embedding model to use for vectorization.",
    )
    embedding_hf_vector_dimensions: int = Field(
        default=1024,
        description="Number of dimensions for the HuggingFace embedding vectors.",
    )

    # Sparse embedding configuration
    sparse_embedding_model_name: str = Field(
        default="opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1",
        description=(
            "Name or path of the sparse embedding model"
            " to use for sparse vectorization.",
        ),
    )

    # New methods implementation
    @override
    def get_db_method(self) -> str:
        return self.db_method

    @override
    def get_db_host(self) -> str:
        return self.db_qdrant_host

    @override
    def get_db_port(self) -> int:
        return self.db_qdrant_port

    @override
    def get_db_url(self) -> str:
        return self.db_qdrant_url

    @override
    def get_db_api_key(self) -> str | None:
        return self.db_qdrant_api_key

    @override
    def get_db_collection(self) -> str:
        return self.db_qdrant_collection

    @override
    def get_db_vector_distance(self) -> str:
        return self.db_qdrant_vector_distance

    @override
    def get_db_vector_dimensions(self) -> int:
        return self.db_qdrant_vector_dimensions

    @override
    def get_dense_vector_name(self) -> str:
        return self.db_qdrant_dense_vector_name

    @override
    def get_sparse_vector_name(self) -> str:
        return self.db_qdrant_sparse_vector_name

    @override
    def get_embedding_method(self) -> str:
        return self.embedding_method

    @override
    def get_embedding_model_name(self) -> str:
        return self.embedding_hf_model_name

    @override
    def get_embedding_vector_dimensions(self) -> int:
        return self.embedding_hf_vector_dimensions

    @override
    def get_sparse_embedding_model_name(self) -> str:
        return self.sparse_embedding_model_name

    @model_validator(mode="after")
    def validate_vector_dimensions_consistency(self) -> "Settings":
        """Validates that embedding and Qdrant vector dimensions match.

        Raises:
            ValueError: If dimensions are inconsistent.

        Returns:
            Settings: The validated settings instance.
        """
        if self.embedding_hf_vector_dimensions != self.db_qdrant_vector_dimensions:
            raise ValueError(
                f"Vector dimension mismatch: embedding_hf_vector_dimensions "
                f"({self.embedding_hf_vector_dimensions}) "
                f"must match db_qdrant_vector_dimensions ",
                f"({self.db_qdrant_vector_dimensions}).",
            )
        return self
