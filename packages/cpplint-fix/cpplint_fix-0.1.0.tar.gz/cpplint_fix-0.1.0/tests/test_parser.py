import pytest
from pathlib import Path
import xml.etree.ElementTree as ET
from cpplint_fix.parser import CPPLFailure, CPPLTestcase, CPPLTestsuite

def test_failure():
    failure_msg = "42: Some error message [E123] [1]"

    failure = CPPLFailure.from_message(failure_msg)
    assert isinstance(failure, CPPLFailure)

    assert failure.lineno == 42
    assert failure.message == "Some error message"
    assert failure.code == "E123"
    assert repr(failure) == "CPPLFailure(lineno=42, message='Some error message', code='E123')"
    
    # Test invalid failure element
    invalid_msg = "invalid format"
    with pytest.raises(ValueError):
        CPPLFailure.from_message(invalid_msg)

def test_testcase():
    testcase_elem = ET.Element("testcase", name="test_file.cpp")
    failure_elem = ET.Element("failure")
    failure_elem.text = "42: Some error message [E123] [1]"
    testcase_elem.append(failure_elem)
    
    testcase = CPPLTestcase.from_xml(testcase_elem)
    
    assert testcase.fpath == Path("test_file.cpp")
    assert len(testcase.failures) == 1
    assert testcase.failures[0].lineno == 42
    assert testcase.failures[0].message == "Some error message"
    assert testcase.failures[0].code == "E123"
    
    # Test invalid testcase element
    invalid_elem = ET.Element("not_testcase")
    with pytest.raises(AssertionError):
        CPPLTestcase.from_xml(invalid_elem)
    
    invalid_elem = ET.Element("testcase", name="")
    with pytest.raises(ValueError):
        CPPLTestcase.from_xml(invalid_elem)
        
def test_testsuite():
    testsuite_elem = ET.Element("testsuite")
    testcase_elem = ET.Element("testcase", name="test_file.cpp")
    failure_elem = ET.Element("failure")
    failure_elem.text = "42: Some error message [E123] [1]"
    testcase_elem.append(failure_elem)
    testsuite_elem.append(testcase_elem)
    
    testsuite = CPPLTestsuite.from_xml(testsuite_elem)
    
    assert len(testsuite.testcases) == 1
    assert testsuite.testcases_dict[Path("test_file.cpp")].fpath == Path("test_file.cpp")
    assert len(testsuite.testcases_dict[Path("test_file.cpp")].failures) == 1

    # Test empty testsuite
    empty_suite = CPPLTestsuite.from_xml(ET.Element("testsuite"))
    assert len(empty_suite.testcases) == 0
    
def test_example_xml(examples_path: Path):
    example_file = examples_path / "example.xml"
    assert example_file.exists(), f"Example file {example_file} does not exist"

    testsuite = CPPLTestsuite.from_string(example_file.read_text(encoding="utf-8"))
    assert isinstance(testsuite, CPPLTestsuite), "Parsed object is not of type CPPLTestsuite"

    assert len(testsuite.testcases) > 0, "No test cases found in example XML"
    for testcase in testsuite.testcases:
        assert isinstance(testcase, CPPLTestcase), "Testcase is not of type CPPLTestcase"
        assert len(testcase.failures) >= 0, "Testcase has negative number of failures"
        for failure in testcase.failures:
            assert isinstance(failure, CPPLFailure), "Failure is not of type CPPLFailure"
            assert failure.lineno >= 0, "Failure line number is negative"
            assert failure.message, "Failure message is empty"
            assert failure.code, "Failure code is empty"