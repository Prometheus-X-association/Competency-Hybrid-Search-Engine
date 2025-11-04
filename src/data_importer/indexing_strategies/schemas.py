from enum import StrEnum


class IndexingField(StrEnum):
    """Enum for fields to index in the data import process."""

    TITLE = "title"
    DESCRIPTION = "description"
    CATEGORY = "category"
    KEYWORDS = "keywords"
