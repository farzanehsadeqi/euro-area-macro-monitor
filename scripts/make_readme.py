"""Regenerate README.md with the latest data summary."""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

df = pd.read_parquet("data/processed/observations.parquet")

latest = (
    df.sort_values("date")
      .groupby(["series_key", "source", "frequency"], as_index=False)
      .last()[["series_key", "source", "frequency", "date", "value"]]
      .sort_values("series_key")
)

rows = []
for _, r in latest.iterrows():
    rows.append(
        f"| `{r['series_key']}` | {r['source']} | {r['frequency']} | "
        f"{r['date'].date()} | {r['value']:,.4g} |"
    )

table = "\n".join(rows)
charts = "\n\n".join(
    f"### {r['series_key'].replace('_', ' ')}\n\n"
    f"![{r['series_key']}](output/{r['series_key']}.png)"
    for _, r in latest.iterrows()
)

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

readme = f"""# Euro Area Macro Monitor

Automated ETL pipeline collecting macro and financial indicators from the
ECB Data Portal, Eurostat, and FRED. Runs daily via GitHub Actions.

**Last updated:** {stamp}
**Observations stored:** {len(df):,}

## Indicators

| Series | Source | Frequency | Latest date | Latest value |
|---|---|---|---|---|
{table}

Note on coverage: `hicp_euro_area` uses the EA20 aggregate (20 countries) while
`unemployment_euro_area` uses EA21 (21 countries). Eurostat does not update
area codes across all datasets simultaneously, so the two series do not cover
an identical population.

## How it works
APIs -> fetch -> Parquet (data/processed/) -> DuckDB queries -> charts


- `src/monitor/config.py` — which indicators to collect
- `src/monitor/sources/` — one module per API
- `src/monitor/pipeline.py` — fetch and combine
- `src/monitor/storage.py` — Parquet store with incremental loading
- `.github/workflows/daily-update.yml` — daily scheduled run

Each observation carries a `vintage_date` recording when that figure was first
published, so later revisions do not silently rewrite history.

## Running it yourself

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows; use .venv/bin/activate elsewhere
pip install -r requirements.txt
pip install -e .

cp .env.example .env               # then add your free FRED API key
python scripts/run_pipeline.py
python scripts/make_charts.py
```

A FRED API key is free from https://fredaccount.stlouisfed.org/apikeys
The ECB and Eurostat sources need no key.

## Charts

{charts}

## Development log

See [docs/setup-log.md](docs/setup-log.md) for the build history, design
decisions, and problems encountered.
"""

Path("README.md").write_text(readme, encoding="utf-8")
print(f"README.md updated ({len(readme)} characters)")