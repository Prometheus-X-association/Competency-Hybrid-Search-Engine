from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from data_importer.enums import CompetencyType, Language, Provider
from data_importer.schemas import Competency


class MapperContract(ABC, BaseModel):
    """Abstract class for mapping raw data to a Competency object."""

    provider: Provider
    competency_type: CompetencyType
    lang: Language

    # Pydantic configuration for the MapperContract.
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    @abstractmethod
    def to_competency(self) -> Competency:
        """Convert the raw data to a Competency object.

        Returns:
            Competency: A Competency object with cleaned and formatted fields.
        """
