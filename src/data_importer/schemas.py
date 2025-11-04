from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .enums import CompetencyType, IndexingStrategy, Language, Provider
from .indexing_strategies.schemas import IndexingField


class DataImportRequest(BaseModel):
    """Base model for data import requests."""

    provider: Provider = Field(..., description="Data provider (esco, rome, forma).")
    competency_type: CompetencyType = Field(
        ...,
        description="Type of the item (group, occupation, skill, training).",
    )
    lang: Language = Field(
        ...,
        description="Language of the source item (e.g. 'en', 'fr', 'de').",
    )
    indexing_strategy: IndexingStrategy = Field(
        IndexingStrategy.FIELD_DUPLICATION,
        title="Indexing Strategy",
        description="Indexing strategy to use.",
    )
    fields_to_index: list[IndexingField] | None = Field(
        None,
        title="Fields to Index",
        description=(
            "List of fields to index. If not provided, defaults to "
            "['title', 'description', 'category', 'keywords']."
        ),
    )
    data: dict[str, Any] = Field(
        ...,
        description="Raw JSON payload for one item from the source.",
    )


class Competency(BaseModel):
    """Competency model representing an item from a data source."""

    # Pydantic configuration for the Competency model.
    model_config = ConfigDict(use_enum_values=True)

    code: str = Field(
        ...,
        title="Source Code",
        description="Original code/identifier from the source.",
    )
    lang: Language = Field(..., title="Language", description="Language of this item.")
    type: CompetencyType = Field(
        ...,
        title="Type",
        description="Type (group, occupation, skill, training).",
    )
    provider: Provider = Field(
        ...,
        title="Provider",
        description="Source provider (esco, rome, forma).",
    )
    title: str = Field(
        ...,
        title="Title / Label",
        description="Preferred human-readable label of the item.",
    )
    url: str | None = Field(
        None,
        title="URL",
        description="URL in the source repository (if available).",
    )
    category: str | None = Field(
        None,
        title="Category / Domain",
        description="Broad categories.",
    )
    description: str | None = Field(
        None,
        title="Description / Definition",
        description="Longer description, definition, scopeNote, etc.",
    )
    keywords: list[str] | None = Field(
        None,
        title="Keywords / Alternative Labels",
        description="List of synonyms, altLabels, hiddenLabels, etc.",
    )
    indexed_text: str | None = Field(
        None,
        title="Indexed Text",
        description="Text used for vector-encoding.",
    )
