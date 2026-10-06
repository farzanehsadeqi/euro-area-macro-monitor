"""Fetch everything and save to Parquet."""

from pathlib import Path

from monitor.pipeline import fetch_all

OUTPUT = Path("data/processed/observations.parquet")

df = fetch_all(start="2015-01-01")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUTPUT, index=False)

print()
print(f"Saved {len(df)} rows to {OUTPUT}")
print()
print(df.groupby("series_key")["date"].agg(["min", "max", "count"]))