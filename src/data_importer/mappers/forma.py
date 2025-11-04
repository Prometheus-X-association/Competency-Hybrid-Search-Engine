from typing import override

from mappers.contract import MapperContract

from data_importer.schemas import Competency


class FormaMapper(MapperContract):
    """Mapper for Forma data."""

    code: int
    title: str
    category: str
    NSF: str | None = None
    semantic_field: str | None = None
    synonym: str | None = None
    synonym_job: str | None = None
    specific_terms: str | None = None
    associated_terms: str | None = None
    ROME: str | None = None
    explication_note: str | None = None
    application_note: str | None = None
    indexed_text: str | None = None

    @staticmethod
    def remove_code_from_str(text: str, code_length_to_remove: int) -> str:
        """Remove the code from the beginning of a string.

        Args:
            text (str): The input string.
            code_length_to_remove (int): The length of the code to remove.

        Returns:
            str: The modified string with the code removed.
        """
        return text[(code_length_to_remove + 1) :]

    @override
    def to_competency(self) -> Competency:
        """Convert the FormaMapper instance to a Competency object.

        Returns:
            Competency: A Competency object with cleaned and formatted fields.
        """
        # Clean the title by capitalizing it
        cleaned_title = self.title.capitalize()

        # Remove the 5-digits code from the category field
        cleaned_category = (
            FormaMapper.remove_code_from_str(self.category, 5).capitalize()
            if self.category
            else None
        )

        # Remove the 3-digits code from the NSF field
        cleaned_nsf = (
            FormaMapper.remove_code_from_str(self.NSF, 3) if self.NSF else None
        )

        # Remove the 3-digits code from the semantic_field field
        cleaned_semantic_field = (
            [FormaMapper.remove_code_from_str(self.semantic_field, 3).capitalize()]
            if self.semantic_field
            else []
        )

        # Split the synonym field on '$'
        cleaned_synonym = (
            [s.strip().capitalize() for s in self.synonym.split("$")]
            if self.synonym
            else []
        )

        # Split the synonym_job field on '$'
        cleaned_synonym_job = (
            [s.strip().capitalize() for s in self.synonym_job.split("$")]
            if self.synonym_job
            else []
        )

        # Split the specific_terms field on '$' and
        # remove the 5-digits code from each term
        if not self.specific_terms:
            cleaned_specific_terms = []
        else:
            cleaned_specific_terms = [
                FormaMapper.remove_code_from_str(term.strip(), 5).capitalize()
                for term in self.specific_terms.split("$")
                if term.strip()
            ]

        # Split the associated_terms field on '$' and
        # remove the 5-digits code from each term
        if not self.associated_terms:
            cleaned_associated_terms = []
        else:
            cleaned_associated_terms = [
                FormaMapper.remove_code_from_str(term.strip(), 5).capitalize()
                for term in self.associated_terms.split("$")
                if term.strip()
            ]

        # Split the ROME field on '$' and remove the 5-digits code from each term
        if not self.ROME:
            cleaned_rome = []
        else:
            cleaned_rome = [
                FormaMapper.remove_code_from_str(term.strip(), 5)
                for term in self.ROME.split("$")
                if term.strip()
            ]

        # Create a description from NSF, explication_note, and application_note
        description_parts = []
        if cleaned_nsf:
            description_parts.append(cleaned_nsf)
        if self.explication_note:
            description_parts.append(self.explication_note)
        if self.application_note:
            description_parts.append(self.application_note)
        cleaned_description = ". ".join(
            [
                description_part
                for description_part in description_parts
                if description_part
            ],
        )

        # Create a list of keywords from the cleaned fields
        cleaned_keywords = sorted(
            set(
                cleaned_semantic_field
                + cleaned_synonym
                + cleaned_synonym_job
                + cleaned_specific_terms
                + cleaned_associated_terms
                + cleaned_rome,
            ),
        )
        cleaned_keywords = [
            keyword.capitalize() for keyword in cleaned_keywords if keyword
        ]

        return Competency(
            code=str(self.code),
            lang=self.lang,
            type=self.competency_type,
            provider=self.provider,
            title=cleaned_title,
            url=f"https://formacode.centre-inffo.fr/spip.php?page=thesaurus&fcd_code={self.code}",
            category=cleaned_category,
            description=cleaned_description,
            keywords=cleaned_keywords,
            indexed_text=self.indexed_text or cleaned_title,
        )
