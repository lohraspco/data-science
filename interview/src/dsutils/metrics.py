from __future__ import annotations
import math
from typing import Iterable

def safe_div(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a / b

def rmse(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    err = [(yt - yp) for yt, yp in zip(y_true, y_pred)]
    if not err:
        raise ValueError("Empty sequences")
    return math.sqrt(sum(e * e for e in err) / len(err))
