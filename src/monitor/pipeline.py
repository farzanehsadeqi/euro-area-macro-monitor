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
        df = eurostat.fetch_dataset(item["dataset"], **item["filters"])
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


def fetch_all(start=None):
    """Fetch every configured series and stack them into one table."""
    frames = []

    for item in SERIES:
        try:
            df = fetch_one(item, start=start)
            print(f"{item['name']}: {len(df)} rows")
            frames.append(df)
        except Exception as exc:
            print(f"{item['name']}: FAILED — {exc}")

    if not frames:
        raise RuntimeError("No series could be fetched.")

    return pd.concat(frames, ignore_index=True)