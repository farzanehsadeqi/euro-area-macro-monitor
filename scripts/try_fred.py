"""Test the fred module."""

from monitor.sources.fred import fetch_series

df = fetch_series("CPIAUCSL", start="2024-01-01")

print("Rows:", len(df))
print(df.tail())