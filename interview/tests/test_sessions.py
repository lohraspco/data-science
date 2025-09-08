import pandas as pd
from datetime import datetime, timedelta
from dsutils import build_sessions
from hypothesis import given, strategies as st

def test_sessions_happy_path():
    base = datetime(2025, 1, 1, 9, 0, 0)
    events = pd.DataFrame([
        {"user_id": 1, "ts": base,                 "event": "page_load"},
        {"user_id": 1, "ts": base + timedelta(minutes=30), "event": "page_exit"},
    ])
    out = build_sessions(events)
    assert len(out) == 1
    assert out.loc[0, "session_seconds"] == 1800.0

def test_sessions_latest_load_earliest_exit_same_day():
    base = datetime(2025, 1, 1, 9, 0, 0)
    events = pd.DataFrame([
        {"user_id": 7, "ts": base, "event": "page_load"},
        {"user_id": 7, "ts": base + timedelta(minutes=5), "event": "page_load"},   # later load
        {"user_id": 7, "ts": base + timedelta(minutes=3), "event": "page_exit"},   # earliest exit
    ])
    out = build_sessions(events)
    # latest load is at +5; earliest exit +3 < load → invalid => None
    assert out.iloc[0]["session_seconds"] is None

@given(st.integers(min_value=0, max_value=300))
def test_sessions_non_negative(d):
    base = datetime(2025, 1, 1, 9, 0, 0)
    events = pd.DataFrame([
        {"user_id": "u", "ts": base,                 "event": "page_load"},
        {"user_id": "u", "ts": base + timedelta(seconds=d), "event": "page_exit"},
    ])
    out = build_sessions(events)
    ss = out.iloc[0]["session_seconds"]
    assert ss is None or ss >= 0.0
