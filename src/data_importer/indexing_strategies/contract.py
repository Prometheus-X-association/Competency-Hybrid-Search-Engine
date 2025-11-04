from abc import ABC, abstractmethod

from data_importer.schemas import Competency


class IndexingStrategyContract(ABC):
    """Abstract class for indexing strategies."""

    @abstractmethod
    def expand_competency(self, competency: Competency) -> list[Competency]:
        """Expand a competency into one or more, based on the indexing strategy.

        Args:
            competency (Competency): The competency to expand.

        Returns:
            List[Competency]: A list of expanded competencies.
        """
