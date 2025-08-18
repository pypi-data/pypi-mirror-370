import pytest
from pathlib import Path
from cpplint_fix.edits.base import BaseEdit, EditOperation, EditOperationType
from cpplint_fix.parser import CPPLFailure
from cpplint_fix.source import SourceFile, SourceLine
from cpplint_fix.edits import Edits

def test_base_edit():
    class TestEdit(BaseEdit):
        _error_code = "TEST_EDIT"
        
        def _operations(self, source_file: SourceFile) -> list[EditOperation]:
            return [
                EditOperation(line_number=1, operation_type=EditOperationType.INSERT_AFTER, text="// Test edit applied")
            ]
    
    source = "const int x = 42;"
    source_file = SourceFile(path=Path("test.cpp"), lines=[SourceLine(number=1, line=source)])
    
    edit = TestEdit(CPPLFailure(lineno=1, message="Test failure", code="TEST_EDIT"))
    assert edit.error_code == "TEST_EDIT"
    assert edit.failure.lineno == 1
    assert edit.failure.message == "Test failure"
    
    edit.apply(source_file)
    assert len(source_file.lines) == 1
    assert source_file[1].line == source
    assert source_file[1].insert_after == ["// Test edit applied"]
    
def test_base_edit_invalid_failure():
    class InvalidEdit(BaseEdit):
        _error_code = "INVALID_EDIT"

        def _operations(self, source_file: SourceFile) -> list[EditOperation]:
            return []

    with pytest.raises(AssertionError):
        InvalidEdit(CPPLFailure(lineno=1, message="Invalid failure", code="WRONG_CODE"))

@pytest.mark.parametrize("edit_code", [
    "whitespace/ending_newline"
])    
def test_edits_list(edit_code: str):
    # Check that the edits were scanned correctly
    edit_class = Edits.get(edit_code)
    assert edit_class is not None, f"Edit class for {edit_code} should not be None"
    assert issubclass(edit_class, BaseEdit), f"{edit_class} should be a subclass of BaseEdit"
    
def test_edits_unknown_code():
    # Check that an unknown edit code raises KeyError
    assert Edits.get("unknown/edit_code") is None, "Unknown edit code should return None"