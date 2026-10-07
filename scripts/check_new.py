"""See what the last run actually added."""

import pandas as pd

df = pd.read_parquet("data/processed/observations.parquet")

print("Rows per series:")
print(df.groupby("series_key").size())
print()

print("Latest observation per series:")
latest = df.sort_values("date").groupby("series_key").tail(1)
print(latest[["series_key", "date", "value", "vintage_date"]].to_string(index=False))