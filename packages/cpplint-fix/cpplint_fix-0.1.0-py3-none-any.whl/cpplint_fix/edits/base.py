from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from cpplint_fix.source import SourceFile
from cpplint_fix.parser import CPPLFailure

class EditOperationType(Enum):
    """Enum representing the type of edit operation."""
    INSERT_BEFORE = "insert_before"
    INSERT_AFTER = "insert_after"
    EDIT = "edit"
    DELETE = "delete"
    
@dataclass(frozen=True)
class EditOperation:
    """Represents an edit operation to be applied to a source file."""
    line_number: int
    operation_type: EditOperationType
    text: str = ""

    def __post_init__(self):
        if self.line_number < 1:
            raise ValueError("Line number must be greater than 0")
        if not isinstance(self.text, str):
            raise TypeError("Text must be a string")
    
    def apply(self, source_file: SourceFile) -> None:
        """Apply the edit operation to the given source file."""
        if self.operation_type == EditOperationType.INSERT_BEFORE:
            source_file.insert_before(self.line_number, self.text)
        elif self.operation_type == EditOperationType.INSERT_AFTER:
            source_file.insert_after(self.line_number, self.text)
        elif self.operation_type == EditOperationType.EDIT:
            source_file.edit_line(self.line_number, self.text)
        elif self.operation_type == EditOperationType.DELETE:
            source_file.delete_line(self.line_number)
        else:
            raise ValueError(f"Unknown operation type: {self.operation_type}")

class FailedEditError(Exception):
    pass

class BaseEdit(ABC):
    _error_code: str = "BASE_EDIT"
    _failure: CPPLFailure

    def __init__(self, failure: CPPLFailure):
        self._failure = failure
        assert (
            failure.code == self._error_code
        ), f"Expected error code {self._error_code}, got {failure.code}"

    @property
    def error_code(self) -> str:
        """Returns the error code associated with this edit."""
        return self._error_code

    @property
    def failure(self) -> CPPLFailure:
        """Returns the CPPLFailure associated with this edit."""
        return self._failure

    @abstractmethod
    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns a list of EditOperation instances representing the edits to be applied.
        
        Should throw a FailedEditError if the edit cannot be applied.
        """
        pass
    
    def apply(self, source_file: SourceFile) -> None:
        """Apply the edit to the given source file."""
        operations = self._operations(source_file)
        for operation in operations:
            operation.apply(source_file)
            
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._failure.lineno}: {self.error_code})"