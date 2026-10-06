"""Smoke test for the ECB source. Fetches EUR/USD and prints a summary."""

import logging

from monitor.sources.ecb import fetch_series

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


def main():
    df = fetch_series("EXR", "D.USD.EUR.SP00.A", start="2024-01-01")

    print(f"\nRows:   {len(df)}")
    print(f"Range:  {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Series: {df['series_key'].iloc[0]}\n")
    print(df.head())
    print("...")
    print(df.tail())


if __name__ == "__main__":
    main()