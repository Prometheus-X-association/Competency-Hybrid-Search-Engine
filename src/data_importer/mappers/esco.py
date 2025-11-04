from typing import override

from mappers.contract import MapperContract
from pydantic import Field

from data_importer.schemas import Competency


class EscoMapper(MapperContract):
    """Mapper for ESCO occupations."""

    preferred_label: str = Field(validation_alias="preferredLabel")
    description: str
    concept_uri: str = Field(validation_alias="conceptUri")
    alt_labels: str | None = Field(None, validation_alias="altLabels")
    hidden_labels: str | None = Field(None, validation_alias="hiddenLabels")
    code: str | None = None
    category: str | None = None
    broader_concept_pt: str | None = Field(None, validation_alias="broaderConceptPT")
    indexed_text: str | None = None

    @staticmethod
    def clean_esco_appelation(appelation: str) -> list[str]:
        """Clean and split the appelation string.

        This method is used to handle appelations that may contain multiple roles
        separated by a slash ('/'). It cleans the string and returns a list of roles.

        Args:
            appelation (str): The appelation string to clean and split.

        Returns:
            list[str]: A list of cleaned and split roles.
        """
        if "/" not in appelation:
            return [appelation]

        exactly_two_parts = 2
        parts = [part.strip() for part in appelation.split("/")]
        if len(parts) == exactly_two_parts:
            return [parts[0], parts[1]]
        return [appelation]

    @override
    def to_competency(self) -> Competency:
        """Convert the ESCO occupation mapper instance to a Competency object.

        Returns:
            Competency: A Competency object with cleaned and formatted fields.
        """
        # Capitalize title
        cleaned_title = self.preferred_label.strip().capitalize()

        # Fill the code if not set yet
        if not self.code and self.concept_uri:
            self.code = self.concept_uri.strip()

        # Fill the category if not set yet
        if not self.category and self.broader_concept_pt:
            self.category = self.broader_concept_pt.strip().replace(" | ", ", ")

        # Fill keywords from alt_labels
        keywords = []
        if self.alt_labels:
            # Split alt_labels based on ' | ' or '\n', depending on the input format
            if " | " in self.alt_labels:
                alt_label_list = self.alt_labels.split(" | ")
            elif "\n" in self.alt_labels:
                alt_label_list = self.alt_labels.split("\n")
            else:
                alt_label_list = [self.alt_labels]
            keywords.extend(
                [label.strip() for label in alt_label_list if label.strip()],
            )

        # Fill keywords from hidden_labels if they exist
        if self.hidden_labels:
            hidden_label_list = self.hidden_labels.split("\n")
            keywords.extend(
                [label.strip() for label in hidden_label_list if label.strip()],
            )

        # If the preferred_label has a /, clean it and add to keywords
        cleaned_appelations = EscoMapper.clean_esco_appelation(cleaned_title)
        if len(cleaned_appelations) > 1:
            keywords.extend(cleaned_appelations)

        # Keep only unique keywords
        keywords = sorted(
            {keyword.capitalize() for keyword in keywords if keyword.strip()},
        )

        return Competency(
            code=self.code,
            lang=self.lang,
            type=self.competency_type,
            provider=self.provider,
            title=cleaned_title,
            url=self.concept_uri,
            category=self.category,
            description=self.description,
            keywords=keywords,
            indexed_text=self.indexed_text or cleaned_title,
        )
