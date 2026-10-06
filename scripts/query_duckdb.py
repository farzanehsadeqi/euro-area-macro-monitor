"""Query the Parquet file directly with SQL via DuckDB."""

import duckdb
import pandas as pd

pd.set_option("display.width", 200)
PARQUET = "data/processed/observations.parquet"

con = duckdb.connect()

print("=== Latest value per series ===")
print(con.execute(f"""
    SELECT series_key, frequency, max(date) AS latest_date,
           arg_max(value, date) AS latest_value
    FROM read_parquet('{PARQUET}')
    GROUP BY series_key, frequency
    ORDER BY series_key
""").df())

print()
print("=== Euro area inflation, last 12 months ===")
print(con.execute(f"""
    SELECT date, value
    FROM read_parquet('{PARQUET}')
    WHERE series_key = 'hicp_euro_area'
    ORDER BY date DESC
    LIMIT 12
""").df())

con.close()