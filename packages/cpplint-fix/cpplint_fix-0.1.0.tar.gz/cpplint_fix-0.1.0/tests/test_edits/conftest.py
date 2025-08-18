from pathlib import Path
import pytest
from dataclasses import dataclass

@dataclass(frozen=True)
class EditExample:
    input: Path
    output: Path

@pytest.fixture
def edit_example(examples_path: Path, error_code: str) -> EditExample:
    root_path = examples_path / error_code
    return EditExample(
        input=root_path / "input",
        output=root_path / "output"
    )