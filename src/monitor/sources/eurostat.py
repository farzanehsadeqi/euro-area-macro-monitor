"""Eurostat API. No API key needed.

Dataset codes: https://ec.europa.eu/eurostat/web/main/data/database
"""

from monitor.http import get
import pandas as pd

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def fetch_dataset(dataset, start=None, **filters):
    """Fetch one Eurostat dataset.

    Returns a DataFrame with columns: date, value, series_key.
    """
    url = f"{BASE_URL}/{dataset}"
    params = {"format": "JSON", "lang": "EN", **filters}
    if start:
        params["sinceTimePeriod"] = start[:7]   # Eurostat wants YYYY-MM
        
    response = get(url, params=params)
    response.raise_for_status()
    data = response.json()

    time_index = data["dimension"]["time"]["category"]["index"]
    position_to_date = {position: date for date, position in time_index.items()}

    rows = []
    for position, value in data["value"].items():
        rows.append({"date": position_to_date[int(position)], "value": value})

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["series_key"] = dataset
    df = df.sort_values("date").reset_index(drop=True)

    return df