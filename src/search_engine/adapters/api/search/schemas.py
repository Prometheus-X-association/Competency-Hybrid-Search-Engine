from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from domain.types.competency import Competency


class APIFilterOperator(StrEnum):
    """Enum for supported API filter operators."""

    EQUAL = "eq"
    NOT_EQUAL = "neq"
    IN = "in"
    NOT_IN = "nin"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"


class SearchType(StrEnum):
    """Enum for search types."""

    SEMANTIC = "semantic"
    SPARSE = "sparse"
    HYBRID = "hybrid"


class APIFilter(BaseModel):
    """Model for a single filter for the search endpoint."""

    field: str = Field(..., description="The field of the payload to filter on.")
    operator: APIFilterOperator = Field(..., description="The comparison operator.")
    value: Any = Field(..., description="The value to compare.")


class SearchRequest(BaseModel):
    """Request model for the search endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to encode for the search",
    )
    filters: list[APIFilter] = Field(
        default_factory=list,
        description="Filters to apply to the search",
    )
    top: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    search_type: SearchType = Field(
        default=SearchType.SEMANTIC,
        description="Type of search to perform",
    )


class SearchResultResponse(BaseModel):
    """Search Result for a single entity."""

    identifier: str = Field(..., description="UUID of the entity")
    competency: Competency = Field(..., description="Competency data of the entity")
    score: float = Field(..., description="Similarity score")


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: list[SearchResultResponse]
