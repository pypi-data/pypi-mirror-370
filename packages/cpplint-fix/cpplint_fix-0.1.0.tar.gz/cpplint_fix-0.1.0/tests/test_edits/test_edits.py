from pathlib import Path
import pytest
from cpplint_fix.edits import Edits
from .conftest import EditExample
from cpplint_fix.wrapper import fix_files

@pytest.mark.usefixtures("edit_example")
@pytest.mark.parametrize("error_code", Edits.codes())
def test_edit(edit_example: EditExample, tmp_path: Path):
    assert edit_example is not None
    
    fixed_path = tmp_path / "fixed"
    fixed_path.mkdir(parents=True, exist_ok=True)

    fix_files(edit_example.input, fixed_path)
    
    # Check that all output files match and exist
    for output_file in edit_example.output.glob("*"):
        fixed_file = fixed_path / output_file.name
        assert fixed_file.exists(), f"Output file {fixed_file} does not exist"
        assert fixed_file.read_text() == output_file.read_text(), f"Output file {fixed_file} does not match expected content"