from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Optional

def zscore_normalize(
    df: pd.DataFrame,
    col: str,
    out_col: Optional[str] = None,
    ddof: int = 0
) -> pd.DataFrame:
    """Return a copy with z-scored column; if std==0, z=0 for all rows."""
    out = df.copy()
    m = out[col].mean()
    s = out[col].std(ddof=ddof)
    z = (out[col] - m) / s if s != 0 else 0.0
    out[out_col or f"{col}_z"] = z
    return out

def winsorize(
    s: pd.Series,
    lower: float = 0.01,
    upper: float = 0.99
) -> pd.Series:
    """Clip to empirical quantiles; robust vs outliers."""
    if not (0 <= lower < upper <= 1):
        raise ValueError("Invalid quantile bounds")
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lower=lo, upper=hi)
