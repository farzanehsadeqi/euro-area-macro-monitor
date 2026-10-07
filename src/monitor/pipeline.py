"""Fetch all configured series and combine them into one table."""

from datetime import date

import pandas as pd

from monitor.config import SERIES
from monitor.sources import ecb, eurostat, fred


def fetch_one(item, start=None):
    """Fetch a single configured series."""
    source = item["source"]

    if source == "ecb":
        df = ecb.fetch_series(item["flow"], item["key"], start=start)
    elif source == "eurostat":
        df = eurostat.fetch_dataset(item["dataset"], start=start, **item["filters"])
    elif source == "fred":
        df = fred.fetch_series(item["series_id"], start=start)
    else:
        raise ValueError(f"Unknown source: {source}")

    # Overwrite series_key with our own readable name
    df["series_key"] = item["name"]
    df["source"] = source
    df["frequency"] = item["frequency"]
    df["vintage_date"] = pd.Timestamp(date.today())

    return df


def fetch_all(start=None, last_dates=None):
    """Fetch every configured series.

    If last_dates is given, each series is fetched only from the day after
    its most recent stored observation.
    """
    last_dates = last_dates or {}
    frames = []

    for item in SERIES:
        name = item["name"]

        # Resume from where this series left off, if we have it
        if name in last_dates:
            resume_from = (last_dates[name] + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            resume_from = start

        try:
            df = fetch_one(item, start=resume_from)
            print(f"{name}: {len(df)} rows (from {resume_from})")
            frames.append(df)
        except Exception as exc:
            print(f"{name}: FAILED — {exc}")

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)