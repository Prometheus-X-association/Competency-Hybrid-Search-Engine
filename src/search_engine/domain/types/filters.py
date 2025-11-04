from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class DomainFilterOperator(Enum):
    """Enum for filter operators used in domain filters."""

    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()
    IN = auto()
    NOT_IN = auto()


@dataclass(frozen=True)
class DomainFilter:
    """Representation of a filter condition in the domain."""

    field: str
    operator: DomainFilterOperator
    value: Any
