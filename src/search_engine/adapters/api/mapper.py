from typing import ClassVar

from adapters.api.entity.schemas import EntityResponse
from adapters.api.search.schemas import (
    APIFilter,
    APIFilterOperator,
    SearchResultResponse,
)
from domain.exceptions import ValidationError
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.filters import DomainFilter, DomainFilterOperator
from domain.types.service_models import SearchResult


class ApiCompetencyMapper:
    """Mapper class for converting between domain Competency and adapters object."""

    @staticmethod
    def domain_to_adapter(competency: Competency) -> Competency:
        """Converts a domain Competency object to a Competency.

        Args:
            competency (Competency): The domain Competency object.

        Returns:
            Competency: The corresponding Competency.
        """
        return Competency(
            code=competency.code,
            lang=competency.lang,
            type=competency.type,
            provider=competency.provider,
            title=competency.title,
            url=competency.url,
            category=competency.category,
            description=competency.description,
        )


class ApiEntityMapper:
    """Mapper class for converting between Entity and adapters objects."""

    @staticmethod
    def domain_to_adapter(entity: Entity) -> EntityResponse:
        """Converts a domain Entity object to an EntityResponse schema.

        Args:
            entity (Entity): The domain Entity object.

        Returns:
            EntityResponse: The corresponding EntityResponse schema.
        """
        return EntityResponse(
            identifier=entity.identifier,
            competency=ApiCompetencyMapper.domain_to_adapter(entity.competency),
        )


class ApiSearchResultMapper:
    """Mapper class for converting between SearchResult and adapters objects."""

    @classmethod
    def domains_to_adapters(
        cls,
        search_results: list[SearchResult],
    ) -> list[SearchResultResponse]:
        """Maps a list of domain search results to API responses.

        Args:
            search_results (list[SearchResult]): The list of domain search results.

        Returns:
            list[SearchResultResponse]: The corresponding API responses.
        """
        return [cls.domain_to_adapter(result) for result in search_results]

    @staticmethod
    def domain_to_adapter(search_result: SearchResult) -> SearchResultResponse:
        """Maps a domain search result to an API response.

        Args:
            search_result (SearchResult): The domain search result.

        Returns:
            SearchResultResponse: The corresponding API response.
        """
        return SearchResultResponse(
            identifier=str(search_result.entity.identifier),
            competency=ApiCompetencyMapper.domain_to_adapter(
                search_result.entity.competency,
            ),
            score=search_result.score,
        )


class ApiFilterMapper:
    """Mapper class for converting API filters to domain filters."""

    # Mapping constant at class level
    _OPERATOR_MAPPING: ClassVar[dict[APIFilterOperator, DomainFilterOperator]] = {
        APIFilterOperator.EQUAL: DomainFilterOperator.EQUAL,
        APIFilterOperator.NOT_EQUAL: DomainFilterOperator.NOT_EQUAL,
        APIFilterOperator.GREATER_THAN: DomainFilterOperator.GREATER_THAN,
        APIFilterOperator.GREATER_THAN_OR_EQUAL: (
            DomainFilterOperator.GREATER_THAN_OR_EQUAL
        ),
        APIFilterOperator.LESS_THAN: DomainFilterOperator.LESS_THAN,
        APIFilterOperator.LESS_THAN_OR_EQUAL: DomainFilterOperator.LESS_THAN_OR_EQUAL,
        APIFilterOperator.IN: DomainFilterOperator.IN,
        APIFilterOperator.NOT_IN: DomainFilterOperator.NOT_IN,
    }

    @classmethod
    def _get_domain_filter_operator(
        cls,
        api_operator: APIFilterOperator,
    ) -> DomainFilterOperator:
        """Gets the domain filter operator from an API filter operator.

        Args:
            api_operator (APIFilterOperator): The API filter operator.

        Returns:
            DomainFilterOperator: The corresponding domain filter operator.

        Raises:
            ValidationError: If the API operator is not supported.
        """
        domain_operator = cls._OPERATOR_MAPPING.get(api_operator)
        if domain_operator is None:
            raise ValidationError(f"Unsupported API filter operator: {api_operator}")
        return domain_operator

    @classmethod
    def map_api_filters_to_domain(
        cls,
        api_filters: list[APIFilter],
    ) -> list[DomainFilter]:
        """Maps API filters to domain filters.

        Args:
            api_filters (list[APIFilter]): List of API filters to map.

        Returns:
            list[DomainFilter]: List of domain filters.
        """
        return [
            DomainFilter(
                field=f.field,
                operator=cls._get_domain_filter_operator(f.operator),
                value=f.value,
            )
            for f in api_filters
        ]
