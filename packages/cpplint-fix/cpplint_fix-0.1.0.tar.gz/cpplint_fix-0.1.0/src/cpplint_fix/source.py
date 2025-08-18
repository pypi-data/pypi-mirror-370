import os
from enum import Enum
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from dataclasses import dataclass, field
from cpplint import CleansedLines, NestingState, _BlockInfo, _ClassInfo, _NamespaceInfo

class NestingType(Enum):
    """Enum to represent different types of nesting."""
    BLOCK = "block"
    CLASS = "class"
    NAMESPACE = "namespace"
    
    @staticmethod
    def from_object(obj: _BlockInfo) -> "NestingType":
        if isinstance(obj, _ClassInfo):
            return NestingType.CLASS
        elif isinstance(obj, _NamespaceInfo):
            return NestingType.NAMESPACE
        return NestingType.BLOCK


@dataclass(frozen=True)
class SourceLine:
    number: int
    line: str
    block_info: tuple[_BlockInfo, ...] = field(default_factory=tuple)
    insert_before: list[str] = field(default_factory=list)
    insert_after: list[str] = field(default_factory=list)
    edits: list[str|None] = field(default_factory=list)

    def __post_init__(self):
        if self.number <= 0:
            raise ValueError("Line number must be positive")
        if not isinstance(self.line, str):
            raise TypeError("Line must be a string")
        # Strip any newline characters from the line
        object.__setattr__(self, "line", self.line.strip("\n"))

    @property
    def edited_lines(self) -> list[str]:
        """Returns the lines to be inserted before and after the source line."""
        final_line = self.final_line
        if final_line is None:
            return []
        return self.insert_before + [final_line] + self.insert_after

    @property
    def deleted(self) -> bool:
        """Returns True if the line is marked for deletion."""
        return (self.final_line is None)
    
    @property
    def final_line(self) -> str | None:
        """Returns the final line after all edits."""
        if not self.edits:
            return self.line
        # Return the last edit if available, otherwise the original line
        return self.edits[-1]
    
    @property
    def last_block(self) -> _BlockInfo | None:
        if len(self.block_info) == 0:
            return None
        return self.block_info[-1]
    
    @property
    def nesting_level(self) -> int:
        return len(self.block_info)
    
    @property
    def nesting_types(self) -> list[NestingType]:
        return [NestingType.from_object(info) for info in self.block_info]
    
    @property
    def total_class_indent(self) -> int:
        return sum(info.class_indent for info in self.block_info if isinstance(info, _ClassInfo))

    def __repr__(self) -> str:
        return f"{self.number}: {self.line} (+{len(self.insert_before)} before, {len(self.insert_after)} after)"


@dataclass(frozen=True)
class SourceFile:
    """Represents a source file with its lines."""

    path: Path
    lines: list[SourceLine] = field(repr=False)
        
    def _valid_line_number(self, line_number: int) -> None:
        """Check if the line number is valid."""
        if line_number < 1 or line_number > len(self.lines):
            raise IndexError("Line number out of range")

    def insert_before(self, line_number: int, text: str):
        """Insert a line before the specified line number."""
        self._valid_line_number(line_number)
        self.lines[line_number - 1].insert_before.append(text)

    def insert_after(self, line_number: int, text: str):
        """Insert a line after the specified line number."""
        self._valid_line_number(line_number)
        self.lines[line_number - 1].insert_after.append(text)
        
    def edit_line(self, line_number: int, text: str):
        """Edit the line at the specified line number."""
        self._valid_line_number(line_number)
        # Store the edit in the edits list
        self.lines[line_number - 1].edits.append(text)
        
    def delete_line(self, line_number: int):
        """Mark the line at the specified line number for deletion."""
        self._valid_line_number(line_number)
        # Set the final line to None to indicate deletion
        self.lines[line_number - 1].edits.append(None)

    def __getitem__(self, index: int) -> SourceLine:
        """Get a specific line by its index (1-based)."""
        self._valid_line_number(index)
        return self.lines[index - 1]

    def __len__(self) -> int:
        """Returns the number of lines in the source file."""
        return len(self.lines)
    
    def __iter__(self):
        return iter(self.lines)

    def __repr__(self) -> str:
        return f"SourceFile(path={self.path}, lines_count={len(self.lines)})"
    
    def to_file(self, file_path: Path) -> None:
        """Writes the source file to the specified path."""
        all_lines = sum([line.edited_lines for line in self.lines], [])
        with file_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(all_lines))
        
    def apply_edits(self) -> None:
        """Applies all edits to the source file."""
        # First, create a temporary file with all edits applied
        temp_file = NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.to_file(Path(temp_file.name))
        # Now, replace the original file with the temporary file
        temp_file.close()
        os.replace(temp_file.name, self.path)

    @classmethod
    def from_file(cls, file_path: Path) -> "SourceFile":
        """Creates a SourceFile from a given file path."""
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        file_text = file_path.read_text(encoding="utf-8")
        file_lines = file_text.splitlines()
        # If the file ends with a newline, it will be treated as an empty line
        if file_text.endswith("\n"):
            file_lines.append("")

        # CleansedLines requires the placeholder to be 1-indexed
        cleansed_lines = CleansedLines(["// Placeholder"] + file_lines)
        nesting_state = NestingState()
        lines: list[SourceLine] = []
        for i, line in enumerate(file_lines):
            nesting_state.Update(file_path.name, cleansed_lines, i+1, lambda *args: None)
            block_info_tuple = tuple(deepcopy(nesting_state.stack))
            lines.append(SourceLine(number=i+1, line=line, block_info=block_info_tuple))

        return cls(path=file_path, lines=lines)
