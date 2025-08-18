import re
from typing import Callable
from cpplint_fix.edits.base import (
    BaseEdit,
    EditOperation,
    EditOperationType,
    FailedEditError,
)
from cpplint_fix.source import SourceFile
from cpplint import _ClassInfo


class WhitespaceEndingNewline(BaseEdit):
    """Edit to add a missing newline at the end of a file."""

    _error_code = "whitespace/ending_newline"

    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns an edit operation to add a newline at the end of the file."""
        if not source_file.lines or source_file.lines[-1].final_line == "":
            return (
                []
            )  # No operation needed if the last line already ends with a newline

        return [
            EditOperation(
                line_number=len(source_file.lines),
                operation_type=EditOperationType.INSERT_AFTER,
                text="",
            )
        ]


class WhitespaceEndOfLine(BaseEdit):
    """Edit to remove trailing whitespace from lines."""

    _error_code = "whitespace/end_of_line"

    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns edit operations to remove trailing whitespace from lines."""
        line_no = self.failure.lineno
        line_text = source_file[line_no].final_line
        if line_text is None:
            return []
        return [EditOperation(line_no, EditOperationType.EDIT, line_text.rstrip())]


class WhitespaceBlankLine(BaseEdit):
    """Edit to remove blank lines."""

    _error_code = "whitespace/blank_line"

    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns edit operations to remove blank lines."""
        line_no = self.failure.lineno
        return [EditOperation(line_no, EditOperationType.DELETE)]


class WhitespaceIndent(BaseEdit):
    """Edit to fix indentation issues."""

    _error_code = "whitespace/indent"

    # This edit has several variants, so we need to handle them specifically
    _handler_type = Callable[[SourceFile], list[EditOperation]]
    _variants: dict[re.Pattern, _handler_type]

    def __init__(self, failure):
        super().__init__(failure)

        # Assign the variants
        self._variants = {
            re.compile(
                r"(public|private|protected): should be indented \+1 space"
            ): self._fix_accessor_indent,
            re.compile(
                r"Weird number of spaces at line-start."
            ): self._fix_weird_indent,
            re.compile(
                r"Closing brace should be aligned with beginning of class"
            ): self._fix_class_indent,
        }

    def _fix_accessor_indent(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns edit operations to fix indentation."""
        line_no = self.failure.lineno
        source_line = source_file[line_no]
        line = source_line.final_line
        if line is None:
            raise FailedEditError(
                f"Could not fix {self.error_code}: Line {line_no} is missing"
            )
        line = " " * (source_line.total_class_indent + 1) + line.lstrip()
        return [EditOperation(line_no, EditOperationType.EDIT, line)]

    def _fix_weird_indent(self, source_file: SourceFile) -> list[EditOperation]:
        """Fix non-multiple of 4 indent"""
        line_no = self.failure.lineno
        source_line = source_file[line_no]
        line = source_line.final_line
        if line is None:
            return []
        # Get the number of leading spaces and round them up to the nearest multiple of 4
        leading_spaces = len(line) - len(line.lstrip())
        # Check that the problem is still true; could have been fixed otherwise
        if leading_spaces % 2 == 0:
            return []
        
        new_indent = (leading_spaces // 4 + 1) * 4
        new_line = " " * new_indent + line.lstrip()
        return [EditOperation(line_no, EditOperationType.EDIT, new_line)]

    def _fix_class_indent(self, source_file: SourceFile) -> list[EditOperation]:
        """Fix closing brace misaligned with beginning of class"""
        line_no = self.failure.lineno
        if line_no < 2:
            raise FailedEditError(
                f"Could not fix {self.error_code}: Line {line_no} is too early to fix class indent"
            )
        # Find the class info from the previous line
        prev_line = source_file[line_no - 1]
        class_info = prev_line.last_block
        if not isinstance(class_info, _ClassInfo):
            raise FailedEditError(
                f"Could not fix {self.error_code}: Line {line_no} does not have a class block above it"
            )
        class_indent = prev_line.total_class_indent
        line = source_file[line_no].final_line
        if line is None:
            return []
        edited_line = " " * class_indent + line.lstrip()
        return [EditOperation(line_no, EditOperationType.EDIT, edited_line)]

    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        for pattern, handler in self._variants.items():
            if pattern.search(self.failure.message):
                return handler(source_file)
        raise FailedEditError(
            f"Could not fix {self.error_code}: "
            f"No handler found for failure message '{self.failure.message}'"
        )


class WhitespaceComments(BaseEdit):
    """Edit to fix whitespace issues between code and comments."""

    _error_code = "whitespace/comments"

    def _operations(self, source_file: SourceFile) -> list[EditOperation]:
        """Returns edit operations to fix whitespace in comments."""
        line_no = self.failure.lineno
        line_text = source_file[line_no].final_line
        if line_text is None:
            return []
        comment_idx = line_text.find("//")
        code_part = line_text[:comment_idx].rstrip()
        return [
            EditOperation(
                line_no,
                EditOperationType.EDIT,
                f"{code_part}  {line_text[comment_idx:]}",
            )
        ]
