from abc import ABC, abstractmethod

from domain.types.vectors import DenseVector


class EmbeddingServiceContract(ABC):
    """Contract for embedding services."""

    @abstractmethod
    def encode(self, text: str) -> DenseVector:
        """Encodes a text into a vector representation.

        Args:
            text (str): The text to encode into a vector.

        Raises:
            EncodingError: If there is an error during the encoding process.

        Returns:
            DenseVector: The encoded vector representation of the text.
        """
        raise NotImplementedError
