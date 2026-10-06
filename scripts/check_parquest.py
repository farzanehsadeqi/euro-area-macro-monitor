"""Read the Parquet file back and inspect it."""

import pandas as pd

df = pd.read_parquet("data/processed/observations.parquet")

print("Shape:", df.shape)
print()
print("Columns and types:")
print(df.dtypes)
print()
print("Sample rows:")
print(df.sample(5))
print()
print("Vintage date:", df["vintage_date"].unique())