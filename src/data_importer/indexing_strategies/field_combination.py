from typing import override

from indexing_strategies.contract import IndexingStrategyContract
from indexing_strategies.schemas import IndexingField

from data_importer.schemas import Competency


class FieldCombinationStrategy(IndexingStrategyContract):
    """Indexing strategy that combines multiple fields into a single indexed text."""

    def __init__(self, fields: list[IndexingField]) -> None:
        """Initialise the indexing strategy with a list of fields.

        Args:
            fields (List[IndexingField]): List of fields to index.
        """
        self.fields = fields

    @override
    def expand_competency(self, competency: Competency) -> list[Competency]:
        """Expand a competency based on the specified fields.

        Args:
            competency (Competency): The competency to expand.

        Returns:
            List[Competency]: A list of expanded competencies, with a single item.
        """
        parts = []
        for field in self.fields:
            value = getattr(competency, field, "")
            if isinstance(value, list):
                joined_value = ", ".join([str(item) for item in value if item])
                parts.append(joined_value)
            elif value:
                if value.endswith("."):
                    parts.append(value[:-1])
                parts.append(str(value))
        indexed_text = ". ".join(parts).strip()

        return [competency.model_copy(update={"indexed_text": indexed_text})]
