"""Test the eurostat module."""

from monitor.sources.eurostat import fetch_dataset

df = fetch_dataset("prc_hicp_manr", geo="EA20", coicop="CP00", unit="RCH_A")

print("Rows:", len(df))
print(df.tail())