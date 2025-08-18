import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError
from cpplint_fix.source import SourceLine, SourceFile, NestingType, CleansedLines
from cpplint import _BlockInfo, _ClassInfo, _NamespaceInfo

@pytest.mark.parametrize("obj, value", [
    (_BlockInfo(0, True), NestingType.BLOCK),
    (_ClassInfo("Test", True, CleansedLines(["class Test {"]), 0), NestingType.CLASS),
    (_NamespaceInfo(0, True), NestingType.NAMESPACE),
])
def test_nesting_type(obj: _BlockInfo, value: NestingType):
    assert NestingType.from_object(obj) == value

def test_source_line():
    line = SourceLine(number=42, line="int main() { return 0; };\n")
    
    assert line.number == 42
    assert line.line == "int main() { return 0; };"
    assert line.insert_before == []
    assert line.insert_after == []

    with pytest.raises(FrozenInstanceError):
        line.number = 40 # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        line.line = "int main() { return 1; };" # type: ignore
        
    # Try inserting lines before and after
    line.insert_before.append("// This is a comment")
    line.insert_after.append("// End of main function")
    
    assert line.edited_lines == [
        "// This is a comment",
        "int main() { return 0; };",
        "// End of main function"
    ]
    
    with pytest.raises(ValueError):
        SourceLine(number=0, line="Invalid line")
    with pytest.raises(TypeError):
        SourceLine(number=1, line=123) # type: ignore
        
    # Test edits
    src_line = SourceLine(number=1, line="Original line")
    src_line.insert_before.append("Inserted before line")
    src_line.edits.append("Edited line")
    assert src_line.deleted is False
    assert src_line.final_line == "Edited line"
    assert src_line.edited_lines == [
        "Inserted before line",
        "Edited line"
    ]
    
    src_line.edits.append(None)  # Mark for deletion
    assert src_line.deleted is True
    assert src_line.final_line is None
    assert src_line.edited_lines == [] # No lines should be returned after deletion

def test_source_file(tmp_path: Path):
    source_content = """int main() {
    return 0;
}
"""

    source_file_path = tmp_path / "test_source.cpp"
    source_file_path.write_text(source_content)
    
    source_file = SourceFile.from_file(source_file_path)
    assert source_file.path == source_file_path
    assert len(source_file.lines) == 4  # 3 lines + 1 empty line
    assert len(source_file) == 4
    source_lines = source_content.splitlines(keepends=False)

    for (i, line) in enumerate(source_lines, start=1):
        assert source_file[i].number == i
        assert isinstance(source_file[i].line, str)
        assert line == source_file[i].line
    # Last source line should be empty
    assert source_file[4].line == ""

    # Try inserting lines
    source_file.insert_before(2, "// This is a comment before line 2")
    source_file.insert_after(3, "// This is a comment after line 3")
    
    assert source_file[2].insert_before == ["// This is a comment before line 2"]
    assert source_file[3].insert_after == ["// This is a comment after line 3"]

    # Test editing a line
    source_file.edit_line(2, "int main() { return 1; }")
    assert source_file[2].edits == ["int main() { return 1; }"]
    assert source_file[2].final_line == "int main() { return 1; }"

def test_source_file_to_file_and_apply(tmp_path: Path):
    """Test SourceFile.to_file and apply functionality."""
    # Create a test file
    source_content = """
int main() {
    return 0;
}"""
    source_file_path = tmp_path / "test_to_file.cpp"
    source_file_path.write_text(source_content)

    # Load with SourceFile
    source_file = SourceFile.from_file(source_file_path)

    # Insert comments
    source_file.insert_before(2, "// Inserted before line 2")
    source_file.insert_after(3, "// Inserted after line 3")

    # Write to a new file
    output_path = tmp_path / "output.cpp"
    source_file.to_file(output_path)

    # Read back and check contents
    with output_path.open() as f:
        lines = f.read().splitlines(keepends=True)
    expected_lines = [
        "\n",
        "// Inserted before line 2\n",
        "int main() {\n",
        "    return 0;\n",
        "// Inserted after line 3\n",
        "}"
    ]
        
    assert lines == expected_lines
    

    # Test fix: should replace the original file with the edited content
    source_file.apply_edits()
    fixed_lines = source_file_path.read_text().splitlines(keepends=True)
    assert fixed_lines == expected_lines, "Fixed file content does not match expected content"

def test_source_file_block_info(tmp_path: Path):
    source_content = """// Some file
namespace my_space {
    class Something 
    {
        Something() {
            // Implementation
        }
    }
}
// Nothing here
"""

    test_file_path = tmp_path / "test_block_info.cpp"
    with test_file_path.open("w", encoding="utf-8") as f:
        f.write(source_content)
        
    source_file = SourceFile.from_file(test_file_path)
    assert source_file.path == test_file_path
    assert len(source_file.lines) == 11
    
    for i in range(1, len(source_file.lines) + 1):  
        source_line = source_file[i]
        
        if 2 <= i < 9:
            assert source_line.nesting_level >= 1
            assert source_line.nesting_types[0] == NestingType.NAMESPACE
        
        if 3 <= i < 8:
            assert source_line.nesting_level >= 2
            assert source_line.nesting_types[1] == NestingType.CLASS
            assert source_line.total_class_indent == 4  # Indentation level of the class
        if 5 <= i < 7:
            assert source_line.nesting_level == 3
            assert source_line.nesting_types[2] == NestingType.BLOCK
    
    # Namespace extent should start from
