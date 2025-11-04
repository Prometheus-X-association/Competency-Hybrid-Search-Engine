from collections.abc import Callable  # noqa: TC003
from typing import override

from indexing_strategies.contract import IndexingStrategyContract
from indexing_strategies.schemas import IndexingField

from data_importer.schemas import Competency


class FieldDuplicationStrategy(IndexingStrategyContract):
    """Indexing strategy based on specific fields of a competency."""

    def __init__(self, fields: list[IndexingField]) -> None:
        """Initialise the indexing strategy with a list of fields.

        Args:
            fields (List[IndexingField]): List of fields to index.
        """
        self.fields = fields
        self._field_extractors: dict[
            IndexingField,
            Callable[[Competency], list[str]],
        ] = {
            IndexingField.TITLE: lambda comp: [comp.title],
            IndexingField.DESCRIPTION: lambda comp: [comp.description]
            if comp.description
            else [],
            IndexingField.CATEGORY: lambda comp: [comp.category]
            if comp.category
            else [],
            IndexingField.KEYWORDS: lambda comp: comp.keywords or [],
        }

        # Check that all fields have a corresponding extractor
        missing = set(self.fields) - set(self._field_extractors)
        if missing:
            raise ValueError(f"No extractor defined for field(s): {missing}")

    @override
    def expand_competency(self, competency: Competency) -> list[Competency]:
        """Expand a competency based on the specified fields.

        Args:
            competency (Competency): The competency to expand.

        Returns:
            List[Competency]: A list of expanded competencies.
        """
        expanded_competencies = []

        # Iterate over each field
        for field in self.fields:
            # Get the extractor for the field
            extractor = self._field_extractors[field]

            # Extract values from the competency using the extractor
            values = extractor(competency)

            # For each value extracted, create a new competency with the indexed text
            expanded_competencies.extend(
                [
                    competency.model_copy(update={"indexed_text": value})
                    for value in values
                    if value.strip()  # Ensure we only add non-empty values
                ],
            )

        return expanded_competencies
