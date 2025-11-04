from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from domain.types.enums import CompetencyType, Language, Provider


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
        description="Type (occupation, skill, certification).",
    )
    provider: Provider = Field(
        ...,
        title="Provider",
        description="Source provider (esco, rome, forma, forma14).",
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
    metadata: dict[str, Any] | None = Field(
        None,
        title="Metadata of the competency",
        description=(
            "Metadata associated with the competency"
            " such as a scope, access, stats, and so on"
        ),
    )
