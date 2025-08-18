import pytest
from pathlib import Path



@pytest.fixture
def examples_path() -> Path:
    return Path(__file__).parent / "examples"
