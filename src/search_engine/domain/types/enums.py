from enum import StrEnum


class Provider(StrEnum):
    """Enum for all supported data providers."""

    ESCO = "esco"
    ROME = "rome"
    FORMA = "forma"
    FORMA14 = "forma14"


class CompetencyType(StrEnum):
    """Enum for the type of competency to import."""

    OCCUPATION = "occupation"
    SKILL = "skill"
    CERTIFICATION = "certification"


class Language(StrEnum):
    """Enum for supported languages."""

    EN = "en"
    FR = "fr"
