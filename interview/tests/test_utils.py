# tests/test_utils.py
import math
import pytest

def safe_div(a, b):
    if b == 0: raise ZeroDivisionError
    return a / b

@pytest.mark.parametrize("a,b,expected", [
    (6, 3, 2.0),
    (-6, 3, -2.0),
    (5, 2, 2.5),
])
def test_safe_div_happy(a, b, expected):
    assert safe_div(a, b) == expected

def test_safe_div_raises_on_zero():
    with pytest.raises(ZeroDivisionError):
        safe_div(1, 0)

# tests/test_io.py
def test_writes_file(tmp_workdir):
    p = tmp_workdir / "out.txt"
    p.write_text("hello")
    assert p.read_text() == "hello"


# tests/conftest.py
import tempfile
import shutil
import pytest
from pathlib import Path

@pytest.fixture
def tmp_workdir():
    d = Path(tempfile.mkdtemp())
    try:
        yield d
    finally:
        shutil.rmtree(d)
