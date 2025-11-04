"""Test module for search API schemas."""

import pytest
from pydantic import ValidationError

from adapters.api.search.schemas import (
    APIFilter,
    APIFilterOperator,
    SearchRequest,
    SearchResponse,
    SearchResultResponse,
    SearchType,
)
from domain.types.competency import Competency
from domain.types.identifier import Identifier


class TestAPIFilterOperator:
    """Test class for APIFilterOperator enum."""

    def test_filter_operator_values(self) -> None:
        """Test APIFilterOperator enum values."""
        assert APIFilterOperator.EQUAL == "eq"
        assert APIFilterOperator.NOT_EQUAL == "neq"
        assert APIFilterOperator.IN == "in"
        assert APIFilterOperator.NOT_IN == "nin"
        assert APIFilterOperator.GREATER_THAN == "gt"
        assert APIFilterOperator.GREATER_THAN_OR_EQUAL == "gte"
        assert APIFilterOperator.LESS_THAN == "lt"
        assert APIFilterOperator.LESS_THAN_OR_EQUAL == "lte"

    def test_filter_operator_membership(self) -> None:
        """Test APIFilterOperator membership."""
        operators = list(APIFilterOperator)
        assert len(operators) == 8


class TestSearchType:
    """Test class for SearchType enum."""

    def test_search_type_values(self) -> None:
        """Test SearchType enum values."""
        assert SearchType.SEMANTIC == "semantic"
        assert SearchType.SPARSE == "sparse"
        assert SearchType.HYBRID == "hybrid"

    def test_search_type_membership(self) -> None:
        """Test SearchType membership."""
        search_types = list(SearchType)
        assert len(search_types) == 3


class TestAPIFilter:
    """Test class for APIFilter."""

    def test_api_filter_valid(self) -> None:
        """Test valid APIFilter creation."""
        filter_obj = APIFilter(
            field="category",
            operator=APIFilterOperator.EQUAL,
            value="technology",
        )

        assert filter_obj.field == "category"
        assert filter_obj.operator == APIFilterOperator.EQUAL
        assert filter_obj.value == "technology"

    def test_api_filter_missing_fields(self) -> None:
        """Test APIFilter with missing required fields."""
        with pytest.raises(ValidationError):
            APIFilter()

        with pytest.raises(ValidationError):
            APIFilter(field="category")

        with pytest.raises(ValidationError):
            APIFilter(field="category", operator=APIFilterOperator.EQUAL)

    def test_api_filter_invalid_operator(self) -> None:
        """Test APIFilter with invalid operator."""
        with pytest.raises(ValidationError):
            APIFilter(field="category", operator="invalid_operator", value="technology")

    def test_api_filter_serialization(self) -> None:
        """Test APIFilter serialization."""
        filter_obj = APIFilter(
            field="category",
            operator=APIFilterOperator.IN,
            value=["tech", "science"],
        )
        data = filter_obj.model_dump()

        assert data["field"] == "category"
        assert data["operator"] == "in"
        assert data["value"] == ["tech", "science"]


class TestSearchRequest:
    """Test class for SearchRequest."""

    def test_search_request_minimal(self) -> None:
        """Test SearchRequest with minimal required fields."""
        request = SearchRequest(text="test query")

        assert request.text == "test query"
        assert request.filters == []
        assert request.top == 10
        assert request.search_type == SearchType.SEMANTIC

    def test_search_request_full(self) -> None:
        """Test SearchRequest with all fields."""
        filters = [
            APIFilter(
                field="category",
                operator=APIFilterOperator.EQUAL,
                value="technology",
            ),
        ]

        request = SearchRequest(
            text="test query",
            filters=filters,
            top=20,
            search_type=SearchType.HYBRID,
        )

        assert request.text == "test query"
        assert request.filters == filters
        assert request.top == 20
        assert request.search_type == SearchType.HYBRID

    def test_search_request_missing_text(self) -> None:
        """Test SearchRequest with missing text."""
        with pytest.raises(ValidationError):
            SearchRequest()

    def test_search_request_invalid_top_range(self) -> None:
        """Test SearchRequest with top out of valid range."""
        with pytest.raises(ValidationError):
            SearchRequest(text="test", top=0)

        with pytest.raises(ValidationError):
            SearchRequest(text="test", top=101)

    def test_search_request_invalid_search_type(self) -> None:
        """Test SearchRequest with invalid search type."""
        with pytest.raises(ValidationError):
            SearchRequest(text="test", search_type="invalid_type")

    def test_search_request_serialization(self) -> None:
        """Test SearchRequest serialization."""
        request = SearchRequest(
            text="test query",
            top=15,
            search_type=SearchType.SPARSE,
        )
        data = request.model_dump()

        assert data["text"] == "test query"
        assert data["top"] == 15
        assert data["search_type"] == "sparse"


class TestSearchResultResponse:
    """Test class for SearchResultResponse."""

    def test_search_result_response_valid(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test valid SearchResultResponse creation."""
        response = SearchResultResponse(
            identifier=str(sample_identifier),
            competency=sample_competency,
            score=0.95,
        )

        assert response.identifier == str(sample_identifier)
        assert response.competency == sample_competency
        assert response.score == 0.95

    def test_search_result_response_missing_fields(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test SearchResultResponse with missing fields."""
        identifier = str(sample_identifier)

        with pytest.raises(ValidationError):
            SearchResultResponse()

        with pytest.raises(ValidationError):
            SearchResultResponse(identifier=identifier)

        with pytest.raises(ValidationError):
            SearchResultResponse(identifier=identifier, competency=sample_competency)

        with pytest.raises(ValidationError):
            SearchResultResponse(competency=sample_competency, score=0.95)

    def test_search_result_response_serialization(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test SearchResultResponse serialization."""
        identifier = str(sample_identifier)
        response = SearchResultResponse(
            identifier=identifier,
            competency=sample_competency,
            score=0.85,
        )
        data = response.model_dump()

        assert data["identifier"] == identifier
        assert data["score"] == 0.85
        assert "competency" in data


class TestSearchResponse:
    """Test class for SearchResponse."""

    def test_search_response_empty(self) -> None:
        """Test SearchResponse with empty results."""
        response = SearchResponse(results=[])

        assert response.results == []

    def test_search_response_with_results(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test SearchResponse with results."""
        result = SearchResultResponse(
            identifier=str(sample_identifier),
            competency=sample_competency,
            score=0.9,
        )

        response = SearchResponse(results=[result])

        assert len(response.results) == 1
        assert response.results[0] == result

    def test_search_response_serialization(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test SearchResponse serialization."""
        result = SearchResultResponse(
            identifier=str(sample_identifier),
            competency=sample_competency,
            score=0.8,
        )

        response = SearchResponse(results=[result])
        data = response.model_dump()

        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["score"] == 0.8
        assert data["results"][0]["identifier"] == str(sample_identifier)
