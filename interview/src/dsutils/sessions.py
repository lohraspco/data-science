from __future__ import annotations
import pandas as pd

def build_sessions(events: pd.DataFrame) -> pd.DataFrame:
    """
    Given events with columns:
      user_id (int/str), ts (datetime-like), event (str: {'page_load','page_exit'})
    For each user_id, day, keep latest page_load and earliest page_exit
    where exit >= load; compute session_seconds.
    """
    df = events.copy()
    df["date"] = pd.to_datetime(df["ts"]).dt.date

    loads = (df[df["event"] == "page_load"]
             .sort_values("ts")
             .groupby(["user_id", "date"], as_index=False)
             .tail(1)
             .rename(columns={"ts": "load_ts"}))

    exits = (df[df["event"] == "page_exit"]
             .sort_values("ts")
             .groupby(["user_id", "date"], as_index=False)
             .head(1)
             .rename(columns={"ts": "exit_ts"}))

    pair = loads.merge(exits, on=["user_id", "date"], how="left")

    pair["session_seconds"] = (
        (pair["exit_ts"] - pair["load_ts"]).dt.total_seconds()
        .where(pair["exit_ts"].notna(), other=None)
        .where(lambda x: (x is None) or True)  # keep None if no exit
    )

    # Invalidate negative durations (bad ordering)
    pair.loc[pair["session_seconds"].notna() & (pair["session_seconds"] < 0), "session_seconds"] = None

    return pair[["user_id", "date", "load_ts", "exit_ts", "session_seconds"]]
