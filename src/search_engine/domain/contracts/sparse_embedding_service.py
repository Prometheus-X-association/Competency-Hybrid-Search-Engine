from abc import ABC, abstractmethod

from domain.types.vectors import SparseVector


class SparseEmbeddingServiceContract(ABC):
    """Contract for sparse embedding services."""

    @abstractmethod
    def encode(self, text: str) -> SparseVector:
        """Encodes a text into a sparse vector representation.

        Args:
            text (str): The text to encode.

        Raises:
            EncodingError: If there is an error during the encoding process.

        Returns:
            SparseVector: The sparse vector representation.
        """
        raise NotImplementedError
