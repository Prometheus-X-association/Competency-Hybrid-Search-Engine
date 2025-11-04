"""Test module for vector types."""

from domain.types.vectors import DenseVector, SparseVector, VectorName


class TestDenseVector:
    """Test class for DenseVector."""

    def test_dense_vector_creation_from_list(self) -> None:
        """Test DenseVector creation from list."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        dense_vector = DenseVector(values=values)

        assert dense_vector.values == values
        assert isinstance(dense_vector.values, list)
        assert len(dense_vector.values) == 5

    def test_dense_vector_empty_values(self) -> None:
        """Test DenseVector with empty values."""
        dense_vector = DenseVector(values=[])

        assert dense_vector.values == []
        assert len(dense_vector.values) == 0


class TestSparseVector:
    """Test class for SparseVector."""

    def test_sparse_vector_creation(self) -> None:
        """Test SparseVector creation."""
        indices = [0, 2, 4]
        values = [1.0, 3.0, 5.0]
        sparse_vector = SparseVector(indices=indices, values=values)

        assert sparse_vector.indices == indices
        assert sparse_vector.values == values
        assert len(sparse_vector.indices) == len(sparse_vector.values)

    def test_sparse_vector_empty(self) -> None:
        """Test empty SparseVector creation."""
        sparse_vector = SparseVector(indices=[], values=[])

        assert sparse_vector.indices == []
        assert sparse_vector.values == []
        assert len(sparse_vector.indices) == 0
        assert len(sparse_vector.values) == 0


class TestVectorName:
    """Test class for VectorName enum."""

    def test_vector_name_dense_value(self) -> None:
        """Test that DENSE vector name has correct value."""
        assert VectorName.DENSE == "dense"
        assert VectorName.DENSE.value == "dense"

    def test_vector_name_sparse_value(self) -> None:
        """Test that SPARSE vector name has correct value."""
        assert VectorName.SPARSE == "sparse"
        assert VectorName.SPARSE.value == "sparse"

    def test_vector_name_membership(self) -> None:
        """Test VectorName enum membership."""
        assert VectorName.DENSE in VectorName
        assert VectorName.SPARSE in VectorName

    def test_vector_name_count(self) -> None:
        """Test that VectorName has exactly 2 members."""
        assert len(VectorName) == 2

    def test_vector_name_from_string(self) -> None:
        """Test creating VectorName from string value."""
        assert VectorName("dense") == VectorName.DENSE
        assert VectorName("sparse") == VectorName.SPARSE

    def test_vector_name_str_representation(self) -> None:
        """Test string representation of VectorName."""
        assert str(VectorName.DENSE) == "dense"
        assert str(VectorName.SPARSE) == "sparse"
