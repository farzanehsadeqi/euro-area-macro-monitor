"""ECB Data Portal — SDMX 2.1 REST API. No API key required.

Series keys can be found at https://data.ecb.europa.eu/data/datasets
On the portal a key looks like EXR.D.USD.EUR.SP00.A, where EXR is the
dataflow and D.USD.EUR.SP00.A is the series key.
"""

import io

import pandas as pd

from monitor.http import get

BASE_URL = "https://data-api.ecb.europa.eu/service/data"


def fetch_series(flow, key, start=None, end=None):
    """Fetch one ECB series and return a tidy DataFrame.

    Returns columns: date (datetime64), value (float), series_key (str).
    """
    url = f"{BASE_URL}/{flow}/{key}"
    params = {"format": "csvdata"}
    if start:
        params["startPeriod"] = start
    if end:
        params["endPeriod"] = end

    response = get(url, params=params)
    raw = pd.read_csv(io.StringIO(response.text))

    expected = {"TIME_PERIOD", "OBS_VALUE"}
    missing = expected - set(raw.columns)
    if missing:
        raise ValueError(
            f"Unexpected ECB response for {flow}/{key}: missing {missing}. "
            f"Columns returned: {list(raw.columns)}"
        )

    df = pd.DataFrame({
        "date": pd.to_datetime(raw["TIME_PERIOD"]),
        "value": pd.to_numeric(raw["OBS_VALUE"], errors="coerce"),
        "series_key": f"{flow}.{key}",
    })

    return df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)