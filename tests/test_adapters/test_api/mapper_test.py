"""Test module for API mappers."""

import pytest
from pytest_mock import MockerFixture

from adapters.api.entity.schemas import EntityResponse
from adapters.api.mapper import (
    ApiCompetencyMapper,
    ApiEntityMapper,
    ApiFilterMapper,
    ApiSearchResultMapper,
)
from adapters.api.search.schemas import (
    APIFilter,
    APIFilterOperator,
    SearchResultResponse,
)
from domain.exceptions import ValidationError
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.filters import DomainFilterOperator
from domain.types.service_models import SearchResult


class TestApiCompetencyMapper:
    """Test class for ApiCompetencyMapper."""

    def test_domain_to_adapter(self, sample_competency: Competency) -> None:
        """Test converting domain competency to adapter."""
        result = ApiCompetencyMapper.domain_to_adapter(sample_competency)

        assert isinstance(result, Competency)
        assert result.code == sample_competency.code
        assert result.lang == sample_competency.lang
        assert result.type == sample_competency.type
        assert result.provider == sample_competency.provider
        assert result.title == sample_competency.title
        assert result.url == sample_competency.url
        assert result.category == sample_competency.category
        assert result.description == sample_competency.description


class TestApiEntityMapper:
    """Test class for ApiEntityMapper."""

    def test_domain_to_adapter(self, sample_entity: Entity) -> None:
        """Test converting domain entity to adapter."""
        result = ApiEntityMapper.domain_to_adapter(sample_entity)

        assert isinstance(result, EntityResponse)
        assert result.identifier == sample_entity.identifier
        assert isinstance(result.competency, Competency)


class TestApiSearchResultMapper:
    """Test class for ApiSearchResultMapper."""

    def test_domain_to_adapter(self, sample_search_result: SearchResult) -> None:
        """Test converting domain search result to adapter."""
        result = ApiSearchResultMapper.domain_to_adapter(sample_search_result)

        assert isinstance(result, SearchResultResponse)
        assert result.identifier == str(sample_search_result.entity.identifier)
        assert isinstance(result.competency, Competency)
        assert result.score == sample_search_result.score

    def test_domains_to_adapters(self, sample_search_result: SearchResult) -> None:
        """Test converting list of domain search results to adapters."""
        search_results = [sample_search_result, sample_search_result]

        results = ApiSearchResultMapper.domains_to_adapters(search_results)

        assert len(results) == len(search_results)
        assert all(isinstance(r, SearchResultResponse) for r in results)
        assert all(
            r.identifier == str(sample_search_result.entity.identifier) for r in results
        )
        assert all(isinstance(r.competency, Competency) for r in results)
        assert all(r.score == sample_search_result.score for r in results)

    def test_domains_to_adapters_empty(self) -> None:
        """Test converting empty list of search results."""
        results = ApiSearchResultMapper.domains_to_adapters([])

        assert results == []


class TestApiFilterMapper:
    """Test class for ApiFilterMapper."""

    def test_operator_mapping_coverage(self) -> None:
        """Test that all API operators have domain mappings."""
        api_operators = list(APIFilterOperator)
        mapped_operators = list(ApiFilterMapper._OPERATOR_MAPPING.keys())

        assert len(api_operators) == len(mapped_operators)
        for operator in api_operators:
            assert operator in mapped_operators

    def test_get_domain_filter_operator_valid(self) -> None:
        """Test valid operator mapping."""
        for api_op, domain_op in ApiFilterMapper._OPERATOR_MAPPING.items():
            converted_domain_op = ApiFilterMapper._get_domain_filter_operator(api_op)
            assert domain_op == converted_domain_op

    def test_get_domain_filter_operator_invalid(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test invalid operator mapping raises ValidationError."""
        # Temporarily patch the mapping to exclude EQUAL operator
        original_mapping = ApiFilterMapper._OPERATOR_MAPPING.copy()
        modified_mapping = {
            k: v for k, v in original_mapping.items() if k != APIFilterOperator.EQUAL
        }

        mocker.patch.object(
            ApiFilterMapper,
            "_OPERATOR_MAPPING",
            modified_mapping,
        )

        # Test that missing operator raises ValidationError
        with pytest.raises(
            ValidationError,
            match="Unsupported API filter operator",
        ):
            ApiFilterMapper._get_domain_filter_operator(
                APIFilterOperator.EQUAL,
            )

    def test_map_api_filters_to_domain_multiple(self) -> None:
        """Test mapping multiple API filters to domain."""
        api_filters = [
            APIFilter(
                field="category",
                operator=APIFilterOperator.EQUAL,
                value="technology",
            ),
            APIFilter(
                field="score",
                operator=APIFilterOperator.GREATER_THAN,
                value=0.5,
            ),
            APIFilter(
                field="tags",
                operator=APIFilterOperator.IN,
                value=["python", "programming"],
            ),
        ]

        domain_filters = ApiFilterMapper.map_api_filters_to_domain(api_filters)

        assert len(domain_filters) == len(api_filters)

        # Check first filter
        assert domain_filters[0].field == api_filters[0].field
        assert domain_filters[0].operator == DomainFilterOperator.EQUAL
        assert domain_filters[0].value == api_filters[0].value

        # Check second filter
        assert domain_filters[1].field == api_filters[1].field
        assert domain_filters[1].operator == DomainFilterOperator.GREATER_THAN
        assert domain_filters[1].value == api_filters[1].value

        # Check third filter
        assert domain_filters[2].field == api_filters[2].field
        assert domain_filters[2].operator == DomainFilterOperator.IN
        assert domain_filters[2].value == api_filters[2].value

    def test_map_api_filters_to_domain_empty(self) -> None:
        """Test mapping empty list of API filters."""
        domain_filters = ApiFilterMapper.map_api_filters_to_domain([])

        assert domain_filters == []

    def test_all_operator_mappings(self) -> None:
        """Test all operator mappings work correctly."""
        operator_pairs = [
            (APIFilterOperator.EQUAL, DomainFilterOperator.EQUAL),
            (APIFilterOperator.NOT_EQUAL, DomainFilterOperator.NOT_EQUAL),
            (APIFilterOperator.GREATER_THAN, DomainFilterOperator.GREATER_THAN),
            (
                APIFilterOperator.GREATER_THAN_OR_EQUAL,
                DomainFilterOperator.GREATER_THAN_OR_EQUAL,
            ),
            (APIFilterOperator.LESS_THAN, DomainFilterOperator.LESS_THAN),
            (
                APIFilterOperator.LESS_THAN_OR_EQUAL,
                DomainFilterOperator.LESS_THAN_OR_EQUAL,
            ),
            (APIFilterOperator.IN, DomainFilterOperator.IN),
            (APIFilterOperator.NOT_IN, DomainFilterOperator.NOT_IN),
        ]

        for api_op, expected_domain_op in operator_pairs:
            api_filter = APIFilter(
                field="test_field",
                operator=api_op,
                value="test_value",
            )

            domain_filters = ApiFilterMapper.map_api_filters_to_domain([api_filter])
            assert len(domain_filters) == 1
            assert domain_filters[0].field == api_filter.field
            assert domain_filters[0].operator == expected_domain_op
            assert domain_filters[0].value == api_filter.value
