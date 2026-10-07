"""ECB Data Portal. No API key needed.

Series keys: https://data.ecb.europa.eu/data/datasets
On the portal a key looks like EXR.D.USD.EUR.SP00.A, where EXR is the
dataflow and D.USD.EUR.SP00.A is the series key.
"""

import io

from monitor.http import get
import pandas as pd

BASE_URL = "https://data-api.ecb.europa.eu/service/data"


def fetch_series(flow, key, start=None):
    """Fetch one ECB series.

    Returns a DataFrame with columns: date, value, series_key.
    """
    url = f"{BASE_URL}/{flow}/{key}"
    params = {"format": "csvdata"}
    if start:
        params["startPeriod"] = start

    response = get(url, params=params)

    # An empty range can come back as 400 or 404; that is not a failure
    if response.status_code in (400, 404):
        return pd.DataFrame(columns=["date", "value", "series_key"])

    response.raise_for_status()
    
    if not response.text.strip():
        return pd.DataFrame(columns=["date", "value", "series_key"])

    raw = pd.read_csv(io.StringIO(response.text))

    df = pd.DataFrame({
        "date": pd.to_datetime(raw["TIME_PERIOD"]),
        "value": pd.to_numeric(raw["OBS_VALUE"], errors="coerce"),
        "series_key": f"{flow}.{key}",
    })

    return df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)