import re
from pathlib import Path
from dataclasses import dataclass
import xml.etree.ElementTree as XMLET


@dataclass(frozen=True)
class CPPLFailure:
    lineno: int
    message: str
    code: str
    
    _failre = re.compile(r"^(?P<lineno>\d+):\s*(?P<message>.*)\s*\[(?P<code>.*)\] \[\d+\]$")
    
    @classmethod
    def from_message(cls, raw_msg: str) -> "CPPLFailure":
        """Creates a CPPLFailure from a raw message string."""
        _failm = cls._failre.match(raw_msg)
        if not _failm:
            raise ValueError(f"Invalid failure message: '{raw_msg}'")
        lineno = int(_failm.group("lineno"))
        message = _failm.group("message").strip()
        code = _failm.group("code")
        return cls(lineno=lineno, message=message, code=code)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lineno={self.lineno}, message='{self.message}', code='{self.code}')"


@dataclass(frozen=True)
class CPPLTestcase:
    fpath: Path
    failures: list[CPPLFailure]

    @classmethod
    def from_xml(cls, elem: XMLET.Element) -> "CPPLTestcase":
        assert elem.tag == "testcase", f"Expected 'testcase' tag, got {elem.tag}"
        fpath = elem.attrib.get("name", "")
        if not fpath:
            raise ValueError("Testcase name cannot be empty")
        failures: list[CPPLFailure] = []
        for child in elem:
            if child.tag != "failure":
                raise ValueError(f"Unexpected tag '{child.tag}' in testcase")
            # Get the inner text of the failure element
            if not child.text:
                raise ValueError("Failure element cannot be empty")
            failure_msgs = child.text.splitlines()
            if not failure_msgs:
                raise ValueError("Failure element cannot be empty")
            # Create CPPLFailure objects from the failure messages
            failures.extend(CPPLFailure.from_message(msg) for msg in failure_msgs)

        return cls(fpath=Path(fpath), failures=failures)

    @property
    def failures_dict(self) -> dict[int, list[CPPLFailure]]:
        """Returns a dictionary grouping failures by line number."""
        if not self.failures:
            return {}
        fdict = {}
        for fail in self.failures:
            flist: list[CPPLFailure] = fdict.setdefault(fail.lineno, [])
            flist.append(fail)
        return fdict

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(fpath={self.fpath}, failures_count={len(self.failures)})"
    

@dataclass(frozen=True)
class CPPLTestsuite:
    testcases: list[CPPLTestcase]

    @property
    def testcases_dict(self) -> dict[Path, CPPLTestcase]:
        """Returns a dictionary mapping file paths to Testcase objects."""
        return {tc.fpath: tc for tc in self.testcases}
    
    @property
    def total_failures(self) -> int:
        """Returns the total number of failures across all testcases."""
        return sum(len(tc.failures) for tc in self.testcases)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(testcases_count={len(self.testcases)})"

    @classmethod
    def from_xml(cls, elem: XMLET.Element) -> "CPPLTestsuite":
        assert elem.tag == "testsuite", f"Expected 'testsuite' tag, got {elem.tag}"
        testcases = [CPPLTestcase.from_xml(child) for child in elem]
        return cls(testcases=testcases)

    @classmethod
    def from_string(cls, xml_string: str) -> "CPPLTestsuite":
        """Creates a CPPLTestsuite from an XML string."""
        root = XMLET.fromstring(xml_string)
        return cls.from_xml(root)