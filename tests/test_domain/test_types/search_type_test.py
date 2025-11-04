"""Test module for SearchType enum."""

import pytest

from domain.types.search_type import SearchType


class TestSearchType:
    """Test class for SearchType enum."""

    def test_search_type_values(self) -> None:
        """Test SearchType enum values."""
        assert SearchType.SEMANTIC.value == "semantic"
        assert SearchType.SPARSE.value == "sparse"
        assert SearchType.HYBRID.value == "hybrid"

    def test_search_type_members(self) -> None:
        """Test SearchType enum members."""
        assert SearchType.SEMANTIC in SearchType
        assert SearchType.SPARSE in SearchType
        assert SearchType.HYBRID in SearchType

    def test_search_type_from_string(self) -> None:
        """Test creating SearchType from string values."""
        assert SearchType("semantic") == SearchType.SEMANTIC
        assert SearchType("sparse") == SearchType.SPARSE
        assert SearchType("hybrid") == SearchType.HYBRID

    def test_search_type_invalid_value(self) -> None:
        """Test SearchType with invalid value."""
        with pytest.raises(ValueError):  # noqa: PT011
            SearchType("invalid")

    def test_search_type_equality(self) -> None:
        """Test SearchType equality comparison."""
        assert SearchType.SEMANTIC == SearchType.SEMANTIC
        assert SearchType.SPARSE == SearchType.SPARSE
        assert SearchType.HYBRID == SearchType.HYBRID

        assert SearchType.SEMANTIC != SearchType.SPARSE
        assert SearchType.SPARSE != SearchType.HYBRID
        assert SearchType.SEMANTIC != SearchType.HYBRID

    def test_search_type_string_representation(self) -> None:
        """Test SearchType string representation."""
        assert str(SearchType.SEMANTIC) == "semantic"
        assert str(SearchType.SPARSE) == "sparse"
        assert str(SearchType.HYBRID) == "hybrid"

    def test_search_type_iteration(self) -> None:
        """Test iterating over SearchType enum."""
        search_types = list(SearchType)

        assert len(search_types) == 3
        assert SearchType.SEMANTIC in search_types
        assert SearchType.SPARSE in search_types
        assert SearchType.HYBRID in search_types

    def test_search_type_name_attribute(self) -> None:
        """Test SearchType name attribute."""
        assert SearchType.SEMANTIC.name == "SEMANTIC"
        assert SearchType.SPARSE.name == "SPARSE"
        assert SearchType.HYBRID.name == "HYBRID"
