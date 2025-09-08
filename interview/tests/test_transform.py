import pandas as pd
import numpy as np
from dsutils import zscore_normalize, winsorize
from hypothesis import given, strategies as st
from hypothesis.extra.pandas import column, data_frames, range_indexes


# Property tests (hypothesis)


@given(
    data_frames(columns=[column("x", elements=st.floats(allow_nan=False, allow_infinity=False))],
                index=range_indexes(min_size=1, max_size=200))
)
def test_zscore_mean_zero(df):
    out = zscore_normalize(df, "x", out_col="z")
    z = out["z"].to_numpy()
    # If variance non-zero, z mean ~= 0 and std ~= 1 (tolerances for float)
    if np.std(z) != 0:
        assert abs(np.mean(z)) < 1e-6
        assert abs(np.std(z) - 1.0) < 1e-6
    else:
        # constant input → all zeros
        assert np.all(z == 0.0)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=10, max_size=500))
def test_winsorize_bounds(xs):
    s = pd.Series(xs)
    w = winsorize(s, 0.05, 0.95)
    lo, hi = s.quantile(0.05), s.quantile(0.95)
    assert (w >= lo - 1e-12).all() and (w <= hi + 1e-12).all()