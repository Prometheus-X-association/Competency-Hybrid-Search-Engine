from typing import override

from logger import LoggerContract
from sentence_transformers.sparse_encoder import SparseEncoder

from adapters.exceptions import EncodingError, ModelLoadingError
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.types.vectors import SparseVector


class HuggingfaceSparseEmbeddingService(SparseEmbeddingServiceContract):
    """Sparse Encoder Service using Hugging Face's SparseEncoder."""

    def __init__(
        self,
        model: SparseEncoder,
        logger: LoggerContract,
    ) -> None:
        """Initialize the HuggingfaceSparseEmbeddingService.

        Args:
            model (SparseEncoder): The HuggingFace
                SparseEncoder model for sparse encoding.
            logger (LoggerContract): The logger instance for logging.
        """
        self.model = model
        self.logger = logger

    @staticmethod
    def load_sparse_encoding_model(model_name: str) -> SparseEncoder:
        """Loads a SparseEncoder model for sparse text embeddings.

        Args:
            model_name (str): The name of the model to load.

        Raises:
            ModelLoadingError: If the model fails to load.

        Returns:
            SparseEncoder: The loaded SparseEncoder model.
        """
        try:
            return SparseEncoder(model_name)
        except Exception as e:
            raise ModelLoadingError(
                f"Failed to load sparse model '{model_name}': {e}",
            ) from e

    @override
    def encode(self, text: str) -> SparseVector:
        """Encodes a text into a sparse vector representation.

        Args:
            text (str): The text to encode.

        Raises:
            EncodingError: If there is an error during the encoding process.

        Returns:
            SparseVector: The sparse vector representation.
        """
        if not self.model:
            raise EncodingError("Sparse model not available")

        self.logger.debug(
            "Encoding text into sparse vector",
            context={"text_length": len(text)},
        )

        try:
            # Get true sparse tensor
            sparse_tensor = self.model.encode(
                text,
                convert_to_tensor=True,
                convert_to_sparse_tensor=True,
            )

            # Convert sparse tensor to indices and values
            if hasattr(sparse_tensor, "coalesce"):
                sparse_tensor = sparse_tensor.coalesce()

            # Extract indices and values from sparse tensor
            indices = sparse_tensor.indices().cpu().numpy()
            values = sparse_tensor.values().cpu().numpy()

            # Create SparseVector object
            sparse_vector = SparseVector(
                indices=(indices.flatten() if indices.ndim > 1 else indices).tolist(),
                values=values.tolist(),
            )
        except Exception as e:
            self.logger.exception(
                "Error during sparse text encoding",
                context={"text_length": len(text), "error": str(e)},
                exc=e,
            )
            raise EncodingError(f"Failed to encode sparse text: {e}") from e

        self.logger.debug(
            "Text encoding completed",
            context={
                "sparse_dimensions": len(sparse_vector.indices),
                "embedding_type": type(sparse_vector),
            },
        )

        return sparse_vector
