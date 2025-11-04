"""Test module for SparseEmbeddingServiceContract."""

import pytest

from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.types.vectors import SparseVector


class TestSparseEmbeddingServiceContract:
    """Test class for SparseEmbeddingServiceContract."""

    def test_sparse_embedding_service_contract_is_abstract(self) -> None:
        """Test that SparseEmbeddingServiceContract cannot be instantiated."""
        with pytest.raises(TypeError):
            SparseEmbeddingServiceContract()

    def test_sparse_embedding_service_contract_encode_method_abstract(self) -> None:
        """Test that encode method is abstract and must be implemented."""

        class IncompleteService(SparseEmbeddingServiceContract):
            """Incomplete implementation missing encode method."""

        with pytest.raises(TypeError):
            IncompleteService()

    def test_sparse_embedding_service_contract_complete_implementation(self) -> None:
        """Test that a complete implementation can be instantiated."""

        class CompleteService(SparseEmbeddingServiceContract):
            """Complete implementation with encode method."""

            def encode(self, text: str) -> SparseVector:
                """Mock implementation."""
                return SparseVector(indices=[0, 1], values=[0.5, 0.3])

        # Should not raise any error
        service = CompleteService()
        result = service.encode("test text")

        assert isinstance(result, SparseVector)
        assert result.indices == [0, 1]
        assert result.values == [0.5, 0.3]
