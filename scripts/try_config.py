"""Check that every configured series actually fetches."""

from monitor.config import SERIES
from monitor.sources import ecb, eurostat, fred


for item in SERIES:
    name = item["name"]
    source = item["source"]

    try:
        if source == "ecb":
            df = ecb.fetch_series(item["flow"], item["key"], start="2024-01-01")
        elif source == "eurostat":
            df = eurostat.fetch_dataset(item["dataset"], **item["filters"])
        elif source == "fred":
            df = fred.fetch_series(item["series_id"], start="2024-01-01")
        else:
            print(f"{name}: unknown source '{source}'")
            continue

        print(f"{name}: OK, {len(df)} rows, last = {df['value'].iloc[-1]}")

    except Exception as exc:
        print(f"{name}: FAILED — {exc}")