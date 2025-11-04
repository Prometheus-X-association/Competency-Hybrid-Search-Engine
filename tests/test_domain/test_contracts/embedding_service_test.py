"""Test module for EmbeddingServiceContract."""

from abc import ABC

import pytest

from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.types.vectors import DenseVector


class TestEmbeddingServiceContract:
    """Test class for EmbeddingServiceContract."""

    def test_embedding_service_contract_is_abstract(self) -> None:
        """Test that EmbeddingServiceContract is abstract."""
        assert issubclass(EmbeddingServiceContract, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            EmbeddingServiceContract()

    def test_embedding_service_contract_abstract_methods(self) -> None:
        """Test that encode method is abstract."""

        # Create a concrete implementation that doesn't implement encode
        class IncompleteEmbeddingService(EmbeddingServiceContract):
            pass

        # Should not be able to instantiate without implementing abstract methods
        with pytest.raises(TypeError):
            IncompleteEmbeddingService()

    def test_embedding_service_contract_concrete_implementation(
        self,
        sample_dense_vector: DenseVector,
    ) -> None:
        """Test concrete implementation of EmbeddingServiceContract."""

        class ConcreteEmbeddingService(EmbeddingServiceContract):
            def encode(self, text: str) -> DenseVector:
                """Simple implementation for testing."""
                return sample_dense_vector

        # Should be able to instantiate concrete implementation
        service = ConcreteEmbeddingService()
        assert isinstance(service, EmbeddingServiceContract)
