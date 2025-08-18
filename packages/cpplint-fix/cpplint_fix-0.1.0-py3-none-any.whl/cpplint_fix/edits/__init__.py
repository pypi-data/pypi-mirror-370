from typing import Type
from .base import BaseEdit, FailedEditError
from .whitespace import (
    WhitespaceEndingNewline,
    WhitespaceEndOfLine,
    WhitespaceBlankLine,
    WhitespaceIndent,
    WhitespaceComments,
)

__all__ = [
    "BaseEdit",
    "FailedEditError",
    "Edits",
    "WhitespaceEndingNewline",
    "WhitespaceEndOfLine",
    "WhitespaceBlankLine",
    "WhitespaceIndent",
    "WhitespaceComments",
]


class Edits:
    """Categorizes and returns all the edits defined within this module."""

    __edits: dict[str, Type[BaseEdit]] = {
        v._error_code: v
        for v in globals().values()
        if isinstance(v, type) and issubclass(v, BaseEdit) and v is not BaseEdit
    }

    @classmethod
    def codes(cls) -> list[str]:
        """Returns a list of all supported edit codes."""
        return list(cls.__edits.keys())

    @classmethod
    def all(cls) -> list[Type[BaseEdit]]:
        """Returns a list of all edit classes."""
        return list(cls.__edits.values())

    @classmethod
    def get(cls, edit_code: str) -> Type[BaseEdit] | None:
        """Returns the edit class for the given error code."""
        if edit_code not in cls.__edits:
            return None
        return cls.__edits[edit_code]
