"""Read and write the Parquet store, with incremental updates."""

from pathlib import Path

import pandas as pd

PARQUET_PATH = Path("data/processed/observations.parquet")


def load_existing():
    """Return what is already stored, or an empty frame if nothing is."""
    if PARQUET_PATH.exists():
        return pd.read_parquet(PARQUET_PATH)
    return pd.DataFrame()


def last_date_per_series(existing):
    """Map each series_key to its most recent date."""
    if existing.empty:
        return {}
    latest = existing.groupby("series_key")["date"].max()
    return latest.to_dict()


def save(new_rows, existing):
    """Combine old and new rows, drop duplicates, and write to disk."""
    if existing.empty:
        combined = new_rows
    else:
        combined = pd.concat([existing, new_rows], ignore_index=True)

    # Keep the most recent vintage when the same observation appears twice
    combined = (
        combined
        .sort_values("vintage_date")
        .drop_duplicates(subset=["series_key", "date"], keep="last")
        .sort_values(["series_key", "date"])
        .reset_index(drop=True)
    )

    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(PARQUET_PATH, index=False)

    return combined