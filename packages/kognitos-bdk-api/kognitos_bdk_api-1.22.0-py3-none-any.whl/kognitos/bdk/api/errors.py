from typing import Optional

from ..reflection.types import ConceptType


class TypeMismatchError(Exception):
    where: str
    expected: Optional[ConceptType]

    def __init__(self, where: str, expected: ConceptType):
        self.where = where
        self.expected = expected
        super().__init__(f"type mismatch on {where} expected {expected}")


class NotFoundError(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
