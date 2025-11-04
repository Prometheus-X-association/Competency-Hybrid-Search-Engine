import re
from typing import override

from mappers.contract import MapperContract
from pydantic import Field

from data_importer.schemas import Competency


class Forma14Mapper(MapperContract):
    """Mapper for Forma data (version 14)."""

    code: int = Field(alias="Code du Terme")
    title: str = Field(alias="Descripteur en typo riche")
    category: str = Field(alias="TG (Terme Générique)")
    semantic_field: str = Field(alias="Champ sémantique")
    synonym: str | None = Field(alias="Synonymes", default=None)
    synonym_job: str | None = Field(alias="Synonymes métier", default=None)
    specific_terms: str | None = Field(alias="TS (Termes Spécifiques)", default=None)
    associated_terms: str | None = Field(alias="TA (Termes Associés)", default=None)
    application_note: str | None = Field(alias="NA (Note d’Application)", default=None)  # noqa: RUF001
    explication_note: str | None = Field(alias="NE (Note d’Explication)", default=None)  # noqa: RUF001
    indexed_text: str | None = None

    @staticmethod
    def remove_code_from_str_start(text: str, code_length_to_remove: int) -> str:
        """Remove a code from the start of a string, following the format "12345 TEXT".

        Args:
            text (str): The input string.
            code_length_to_remove (int): The length of the code to remove.

        Returns:
            str: The modified string with the code removed.
        """
        # Pattern for a numeric code of the specified length,
        # followed by a space at the start
        pattern = f"^\\d{{{code_length_to_remove}}} "

        # If the pattern is found, remove it
        if re.search(pattern, text):
            return text.split(" ", 1)[1]

        return text

    @staticmethod
    def remove_code_from_str_end(text: str, code_length_to_remove: int) -> str:
        """Remove a code from the end of a string, following the format " - 12345".

        Args:
            text (str): The input string.
            code_length_to_remove (int): The length of the code to remove.

        Returns:
            str: The modified string with the code removed.
        """
        # Pattern for " - " followed by a numeric code
        # of the specified length at the end
        pattern = f" - \\d{{{code_length_to_remove}}}$"

        # If the pattern is found, remove it
        if re.search(pattern, text):
            return text.rsplit(" - ", 1)[0]

        return text

    @override
    def to_competency(self) -> Competency:
        """Convert the Forma14Mapper instance to a Competency object.

        Returns:
            Competency: A Competency object with cleaned and formatted fields.
        """
        # Remove the 5-digits code from the category field
        cleaned_category = Forma14Mapper.remove_code_from_str_end(self.category, 5)

        # Remove the 3-digits code from the semantic_field field
        cleaned_semantic_field = Forma14Mapper.remove_code_from_str_start(
            self.semantic_field,
            3,
        ).capitalize()

        # Split the synonym field on '###'
        cleaned_synonym = (
            [s.strip().capitalize() for s in self.synonym.split("###")]
            if self.synonym
            else []
        )

        # Split the synonym_job field on '###'
        cleaned_synonym_job = (
            [s.strip().capitalize() for s in self.synonym_job.split("###")]
            if self.synonym_job
            else []
        )

        # Split the specific_terms field on '###' and
        # remove the 5-digits code from each term
        cleaned_specific_terms = (
            [
                Forma14Mapper.remove_code_from_str_end(term.strip(), 5)
                for term in self.specific_terms.split("###")
                if term.strip()
            ]
            if self.specific_terms
            else []
        )

        # Split the associated_terms field on '$' and
        # remove the 5-digits code from each term
        cleaned_associated_terms = (
            [
                Forma14Mapper.remove_code_from_str_end(term.strip(), 5)
                for term in self.associated_terms.split("$")
                if term.strip()
            ]
            if self.associated_terms
            else []
        )

        # Create a description from explication_note, and application_note
        cleaned_description = ""
        if self.explication_note:
            cleaned_description += self.explication_note
        if self.application_note:
            cleaned_description += self.application_note
        cleaned_description = cleaned_description.strip()

        # Create a list of keywords from the cleaned fields
        cleaned_keywords = sorted(
            {
                cleaned_semantic_field,
                *cleaned_synonym,
                *cleaned_synonym_job,
                *cleaned_specific_terms,
                *cleaned_associated_terms,
            },
        )
        # Filter out empty strings
        cleaned_keywords = [kw for kw in cleaned_keywords if kw.strip()]

        return Competency(
            code=str(self.code),
            lang=self.lang,
            type=self.competency_type,
            provider=self.provider,
            title=self.title,
            url=f"https://centreinffo.mondeca.com/KB/index#Concept:uri=https://centre-inffo.fr/descripteur_formacode/{self.code};tab=props;",
            category=cleaned_category,
            description=cleaned_description,
            keywords=cleaned_keywords,
            indexed_text=self.indexed_text or self.title,
        )
