from pathlib import Path
from cpplint_fix.wrapper import run_cpplint


def test_run_cpplint(examples_path: Path) -> None:
    """Test the run_cpplint function with a sample directory."""
    example_root = examples_path / "whitespace/ending_newline/input"
    
    tsuite = run_cpplint(example_root)
    assert tsuite is not None, "CPPLTestsuite should not be None"
    assert len(tsuite.testcases) == 1, "CPPLTestsuite should contain test cases"
    
    assert tsuite.testcases[0].fpath == Path("main.cpp"), "Test case file path does not match"
    assert len(tsuite.testcases[0].failures) == 1, "Test case should have one failure"
    failure = tsuite.testcases[0].failures[0]
    assert failure.lineno == 5, "Failure line number should be 5"
    assert failure.message == "Could not find a newline character at the end of the file.", "Failure message does not match"
    assert failure.code == "whitespace/ending_newline", "Failure code does not match"
