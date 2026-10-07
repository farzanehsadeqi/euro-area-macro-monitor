"""Fetch new observations and merge them into the Parquet store."""

from monitor.pipeline import fetch_all
from monitor import storage

FULL_HISTORY_FROM = "2015-01-01"

existing = storage.load_existing()
last_dates = storage.last_date_per_series(existing)

if last_dates:
    print("Resuming from stored data:")
    for name, last in sorted(last_dates.items()):
        print(f"  {name}: last stored {last.date()}")
else:
    print("No existing data. Fetching full history.")
print()

new_rows = fetch_all(start=FULL_HISTORY_FROM, last_dates=last_dates)

if new_rows.empty:
    print("\nNothing new fetched.")
else:
    combined = storage.save(new_rows, existing)
    print()
    print(f"Before: {len(existing)} rows")
    print(f"Fetched: {len(new_rows)} rows")
    print(f"After:  {len(combined)} rows")