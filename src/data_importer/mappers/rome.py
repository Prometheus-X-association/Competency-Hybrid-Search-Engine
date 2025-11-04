from typing import override

from mappers.contract import MapperContract

from data_importer.schemas import Competency


class RomeMapper(MapperContract):
    """Mapper for ROME data."""

    code: str
    intitule: str
    category: str
    description: str
    keywords: list[str]
    indexed_text: str | None = None

    @staticmethod
    def clean_rome_appelation(appelation: str) -> list[str]:
        """Clean and split the appelation string.

        This method is used to handle appelations that may contain multiple roles
        separated by a slash ('/'). It cleans the string and returns a list of roles.

        Args:
            appelation (str): The appelation string to clean and split.

        Raises:
            Exception: If an error occurs during processing.

        Returns:
            list[str]: A list of cleaned and split roles.
        """
        # First case, if there is no slash in the appelation,
        # we return the appelation as a single-item list.
        if "/" not in appelation:
            return [appelation]

        # Split the appelation by the slash
        # and ensure there are exactly two parts.
        # If there are more than two parts, we return the original appelation.
        exactly_two_parts = 2
        parties = [p.strip() for p in appelation.split("/")]
        if len(parties) != exactly_two_parts:
            return [appelation]

        gauche, droite = parties

        # Split into words to handle different cases
        mots_gauche = gauche.split()
        mots_droite = droite.split()

        # Second case, common prefix
        # Check if the left part has more words than the right.
        if len(mots_gauche) > len(mots_droite):
            # Le préfixe = différence entre gauche et droite
            nb_mots_prefixe = len(mots_gauche) - len(mots_droite)
            prefixe = " ".join(mots_gauche[:nb_mots_prefixe])

            first = gauche
            second = f"{prefixe} {droite}"

        # Third case, common suffix
        # Check if the right part has more words than the left.
        elif len(mots_droite) > len(mots_gauche):
            # Le suffixe = différence entre droite et gauche
            nb_mots_suffixe = len(mots_droite) - len(mots_gauche)
            suffixe = " ".join(mots_droite[-nb_mots_suffixe:])

            first = f"{gauche} {suffixe}"
            second = droite

        # Forth case, equal separation
        # If both parts have the same number of words, we keep them as they are.
        else:
            first = gauche
            second = droite

        return [first.strip(), second.strip()]

    @override
    def to_competency(self) -> Competency:
        """Convert the RomeMapper instance to a Competency object.

        Returns:
            Competency: A Competency object with cleaned and formatted fields.
        """
        # Clean the keywords by applying the clean_rome_appelation function
        cleaned_keywords = sorted(
            {
                clean_keyword
                for keyword in self.keywords
                for clean_keyword in RomeMapper.clean_rome_appelation(keyword)
            },
        )

        return Competency(
            code=self.code,
            lang=self.lang,
            type=self.competency_type,
            provider=self.provider,
            title=self.intitule,
            url=f"https://candidat.pole-emploi.fr/metierscope/fiche-metier/{self.code}",
            category=self.category,
            description=self.description,
            keywords=cleaned_keywords,
            indexed_text=self.indexed_text or self.intitule,
        )
