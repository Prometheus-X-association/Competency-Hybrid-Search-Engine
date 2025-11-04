from typing import Annotated

from fastapi import APIRouter, Depends

from adapters.api.dependencies import get_entity_service
from adapters.api.mapper import ApiFilterMapper, ApiSearchResultMapper
from adapters.api.search.schemas import (
    SearchRequest,
    SearchResponse,
)
from domain.services.entity_service import EntityService
from domain.types.search_type import SearchType as DomainSearchType

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "/text",
    summary="Search for similar entities with configurable search type",
    response_model_exclude_none=True,
)
async def search(
    req: SearchRequest,
    service: Annotated[EntityService, Depends(get_entity_service)],
) -> SearchResponse:
    """Search for entities based on text input with configurable search type.

    This unified endpoint allows you to search for entities using different
    search strategies: semantic (dense), sparse, or hybrid search.

    Args:
        req (SearchRequest): The request object containing search parameters.
        service (EntityService): The entity service dependency.

    Returns:
        SearchResponse: The response object containing the search results.
    """
    # Convert API filters to domain filters
    domain_filters = ApiFilterMapper.map_api_filters_to_domain(req.filters)

    # Convert API search type to domain search type
    domain_search_type = DomainSearchType(req.search_type.value)

    # Search for similar entities using the specified search type
    results = service.search_by_text_and_filters_with_type(
        text=req.text,
        filters=domain_filters,
        top=req.top,
        search_type=domain_search_type,
    )

    return SearchResponse(
        results=ApiSearchResultMapper.domains_to_adapters(results),
    )
