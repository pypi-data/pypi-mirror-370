from dataclasses import dataclass
from typing import Any, List, Optional

from ..api.noun_phrase import NounPhrase
from .types import ConceptOptionalType, ConceptType


@dataclass
class ConceptDescriptor:
    noun_phrases: List[NounPhrase]
    type: ConceptType
    default_value: Any
    description: Optional[str] = None

    @property
    def is_optional(self) -> bool:
        return isinstance(self.type, ConceptOptionalType)
