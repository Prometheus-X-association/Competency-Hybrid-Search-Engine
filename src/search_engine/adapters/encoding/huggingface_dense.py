from typing import override

from logger import LoggerContract
from sentence_transformers import SentenceTransformer

from adapters.exceptions import EncodingError, ModelLoadingError
from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.types.vectors import DenseVector


class HuggingfaceEmbeddingService(EmbeddingServiceContract):
    """Encoder Service using Hugging Face's SentenceTransformer."""

    def __init__(
        self,
        model: SentenceTransformer,
        logger: LoggerContract,
    ) -> None:
        """Initialize the HuggingfaceEmbeddingService.

        Args:
            model (SentenceTransformer): The Hugging Face model to be used for encoding.
            logger (LoggerContract): The logger instance for logging.
        """
        self.model = model
        self.logger = logger

    @staticmethod
    def load_sentence_embeddings_model(model_name: str) -> SentenceTransformer:
        """Loads a SentenceTransformer model for text embeddings.

        Args:
            model_name (str): The name of the model to load.

        Raises:
            ModelLoadingError: If the model fails to load.

        Returns:
            SentenceTransformer: The loaded SentenceTransformer model.
        """
        try:
            return SentenceTransformer(model_name)
        except Exception as e:
            raise ModelLoadingError(f"Failed to load model '{model_name}': {e}") from e

    @override
    def encode(self, text: str) -> DenseVector:
        """Encodes a text into a vector representation.

        Args:
            text (str): The text to encode into a vector.

        Raises:
            EncodingError: If there is an error during the encoding process.

        Returns:
            DenseVector: The encoded vector representation of the text.
        """
        self.logger.debug(
            "Encoding text into vector",
            context={"text_length": len(text)},
        )

        try:
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            # Convert numpy array to list of floats and wrap in DenseVector
            dense_vector = DenseVector(values=embeddings.tolist())
        except Exception as e:
            self.logger.exception(
                "Error during text encoding",
                context={"text_length": len(text), "error": str(e)},
                exc=e,
            )
            raise EncodingError(f"Failed to encode text: {e}") from e

        self.logger.debug(
            "Text encoding completed",
            context={
                "vector_dimensions": len(dense_vector.values),
                "embedding_type": type(dense_vector),
            },
        )

        return dense_vector
