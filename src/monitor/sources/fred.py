"""FRED (St. Louis Fed). Needs an API key in the .env file."""

import os

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_series(series_id, start=None):
    """Fetch one FRED series.

    Returns a DataFrame with columns: date, value, series_key.
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not found. Check your .env file.")

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }
    if start:
        params["observation_start"] = start

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["observations"])[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["series_key"] = series_id
    df = df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)

    return df