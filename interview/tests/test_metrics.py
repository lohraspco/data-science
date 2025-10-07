import math
import pytest
from dsutils.metrics import rmse, safe_div


@pytest.mark.parametrize("a,b,expected", [(6,3,2.0), (-6,3,-2.0), (5,2,2.5)])
def test_safe_div_ok(a, b, expected):
    assert safe_div(a, b) == pytest.approx(expected)

def  test_safe_dov_zero():
    with pytest.raises(ZeroDivisionError):
        safe_div(6, 0)

def test_rmse_basic():
    assert rmse([1,2,3], [1,2,3]) == pytest.approx(0.0)
    assert rmse([1,3,3], [2,2,2]) == pytest.approx(1)

def test_rmse_empty_sequences():
    with pytest.raises(ValueError):
        rmse([], [])
    with pytest.raises(ValueError):
        rmse([1], [])
    with pytest.raises(ValueError):
        rmse([], [1])