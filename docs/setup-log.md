# Phase 0 — Project Scaffolding

**Project:** `euro-area-macro-monitor`
An automated ETL pipeline collecting macro and financial indicators from the
ECB Data Portal, Eurostat, and FRED.

**Language:** Python
**Location:** `C:\Users\farza\projects\euro-area-macro-monitor`

---

## Why this project

The goal is to demonstrate a *production* data flow — one that runs without
manual intervention and fails loudly when something breaks. That is a different
thing from a notebook that fetched some data once, and it is what job listings
refer to as ETL and automation.

Why start here rather than with a larger analysis project: **the first repository
is where every repo-hygiene mistake happens.** Better that it happens on something
that takes a week. The data-ingestion layer is also reusable in later projects.

---

## Design decisions and reasoning

**Python rather than R.** The source course was in R, but this is a data
engineering project and the scheduling and CI ecosystem is more mature in Python.

**Three data sources, deliberately.** ECB and Eurostat need no API key; FRED does.
Having one keyed source forces proper secret handling (environment variable in
development, GitHub Secrets in automation), which is itself a demonstrable skill.
Having two keyless sources means anyone cloning the repo can run most of it
without registering anywhere.

**Parquet in git, DuckDB not.**
- Parquet is incremental and compressed → committed, makes the repo reproducible.
- DuckDB is a binary file rewritten on every run → git would store a complete new
  copy each time, and the repo would reach gigabytes within a month. It is rebuilt
  from Parquet instead.
- `data/raw/` (raw JSON) is ignored because it is re-fetchable and bulky.

**Project located outside OneDrive.** OneDrive conflicts with the `.git` directory
and virtual environments: file locks, duplicate copies, and occasionally a
corrupted repository.

---

## Steps taken

### 1. Verify prerequisites
```bash
git --version      # 2.54.0.windows.1
python --version   # 3.14.5
```
Note: Python 3.14 is recent and some packages may not yet publish compatible
wheels. In practice no problems occurred.

### 2. Check for pre-existing repositories
```bash
find /c/Users/farza -maxdepth 4 -type d -name ".git" 2>/dev/null
```
Empty output → no existing git repositories, so no cleanup was needed.
(Every git repository has a hidden `.git` directory at its root; this searches
for exactly that.)

### 3. Directory and virtual environment
```bash
mkdir -p /c/Users/farza/projects
cd /c/Users/farza/projects
mkdir euro-area-macro-monitor
cd euro-area-macro-monitor

python -m venv .venv
source .venv/Scripts/activate
```
On Windows the command is `python`, not `python3`, and the path is `Scripts`,
not `bin`.

Verifying the environment is genuinely active:
```bash
python -c "import sys; print(sys.prefix)"
# → C:\Users\farza\projects\euro-area-macro-monitor\.venv
```
If this returns the system Python path, the environment is not active.

### 4. `.gitignore` — written before `git init`

**The rule that drives this ordering: `.gitignore` has no effect on files that
are already tracked.** Commit a large file once and adding it to `.gitignore`
does nothing — it stays in history forever, even after deletion. So the ignore
file must exist before the first commit.

```
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
.env
data/raw/
*.duckdb
*.duckdb.wal
output/*
!output/.gitkeep
```

### 5. Directory structure
```bash
mkdir -p src/monitor/sources data/raw data/processed output tests .github/workflows
touch src/monitor/__init__.py src/monitor/sources/__init__.py
touch data/raw/.gitkeep data/processed/.gitkeep output/.gitkeep
```
- `__init__.py` marks a directory as a Python package so it can be imported.
- `.gitkeep` is needed because **git does not track empty directories** — it only
  sees files.

### 6. Base files
`requirements.txt`, `.env.example`, and `README.md` were created with heredocs:
```bash
cat > filename << 'EOF'
...content...
EOF
```
`.env.example` is committed as a template; the real `.env` never is.

### 7. Install and pin versions
```bash
pip install -r requirements.txt
pip freeze > requirements.lock.txt
```
The "Cache entry deserialization failed" warning was harmless — pip simply could
not reuse its cache and re-downloaded.

Division of labour between the two files:
- `requirements.txt` → what the project needs
- `requirements.lock.txt` → the exact versions known to work (the equivalent of
  `renv` in R)

Installed: pandas 3.0.6, pyarrow 25.0.1, duckdb 1.5.6, matplotlib 3.11.2.
Note that pandas 3 has behavioural changes relative to pandas 2; if example code
found online does not run, this is a likely cause.

### 8. First commit
```bash
git init
git status                 # ← read this before adding
git add .
git status                 # ← last chance to see what enters the commit
git commit -m "Project skeleton: structure, gitignore, dependencies"
git count-objects -vH      # → size: 1.45 KiB
```

1.45 KiB confirms `.venv` was not included. Had it been, this would read in the
hundreds of megabytes.

### 9. Line endings and `.gitattributes`

Adding files produced a warning: `LF will be replaced by CRLF the next time Git
touches it`. Windows writes line endings as two characters (CRLF), Unix as one
(LF); git on Windows converts to LF on commit and back on checkout. The warning
is informational, not an error.

To make the behaviour explicit and silence it:

```bash
cat > .gitattributes << 'EOF'
* text=auto eol=lf
*.png binary
*.parquet binary
*.duckdb binary
EOF
```

The binary declarations matter: if git treated a Parquet file as text and
rewrote its line endings, the file would be corrupted.

### 10. Removing a file after it was committed

The Persian-language copy of this log was committed, then deleted from disk.
`git status` reported it under *Changes not staged for commit*, because a
deletion is itself a change and must be staged like any other.

```bash
git add -A      # -A includes deletions; plain `git add .` may not
git commit -m "Remove Persian setup log from repository"
```

Note that the file remains in *history*. For a document this is irrelevant, but
it is the same mechanism by which a large data file committed once keeps a
repository bloated forever — which is why `.gitignore` was written before the
first commit.

### 11. Rename the default branch

```bash
git branch -M main
```

Git historically creates `master`; GitHub and most current tooling expect `main`.
Renaming before any push is free; renaming after a push is not.

### 12. Final verification

```bash
git ls-files
```

Eleven tracked files, and nothing from `.venv/` or `data/raw/`:

---

## Problems encountered and how they were resolved

### Problem 1 — `output/.gitkeep` never appeared in `git status`

**Cause:** when git ignores a directory outright, it does not descend into it at
all. The `!output/.gitkeep` exception was therefore never evaluated.

**Fix:** change `output/` to `output/*`.
- `output/` means "ignore the directory itself"
- `output/*` means "enter the directory and ignore everything inside" — and
  because git enters it, the negation on the following line is applied.

**Why it mattered:** without the `.gitkeep`, anyone cloning the repo would not
have an `output/` directory, and scripts writing results there would fail.

### Problem 2 — stray `EDF` line inside `.gitignore`

**Cause:** the heredoc terminator was mistyped as `EDF` instead of `EOF`. Since
the terminator did not match, the heredoc continued and that line was written
into the file.

**Fix:** `sed -i '/^EDF$/d' .gitignore`

Harmless in effect — git read it as a pattern matching a nonexistent file named
`EDF` — but removed for cleanliness.

### Clarifications worth recording

- **Phase 0 involves no Python or R file.** The commands run in a terminal
  (Git Bash), not in an editor.
- **`(.venv)` in terminal output** is not part of any command's result; it is the
  shell prompt indicating the virtual environment is active.
- **An empty `ls`** was expected, because `.venv` starts with a dot and is hidden
  from plain `ls`. Use `ls -a`.
- **Confirm location with `pwd`** before any command that creates or deletes
  files. `mkdir` and `rm` in the wrong directory fail silently.

---

## Current state

```
euro-area-macro-monitor/
├── .github/workflows/        (empty)
├── .venv/                    (ignored)
├── data/
│   ├── raw/                  (ignored)
│   └── processed/.gitkeep
├── output/.gitkeep
├── src/monitor/
│   ├── __init__.py
│   └── sources/__init__.py
├── tests/                    (empty)
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── requirements.lock.txt
└── .gitattributes

```


---

## Phase 0 complete

Three commits on `main`, eleven tracked files, repository under 2 KiB.
Not yet pushed to a remote.

# Phase 1 — First API Connection

Goal: fetch one indicator from one source and return a tidy DataFrame.
Source: ECB Data Portal (SDMX 2.1 REST API, no key required).

---

## What was built

### 1. `pyproject.toml` — making the project installable

```bash
pip install -e .
```

`-e` means editable: the code is read from `src/` directly, so changes take
effect immediately without reinstalling.

This is the clean solution to import paths — the alternative is `sys.path`
manipulation inside every script, which breaks as soon as a file moves.
`where = ["src"]` tells setuptools that only `src/` contains package code,
which is why throwaway scripts live in a separate top-level `scripts/`
directory rather than inside the package.

### 2. `src/monitor/http.py` — shared HTTP layer

One `get()` function with retries, exponential backoff, a timeout, and a
descriptive User-Agent. Deliberately separate from any data source, so all
three sources share one implementation: adding throttling later means
changing one place, not three.

Three decisions worth recording:

- **Retries only on transient failures.** A 404 means the URL is wrong and
  repeating it will not help; a 503 means the server is briefly busy and
  retrying is reasonable. `RETRY_ON = {429, 500, 502, 503, 504}`.
- **Honours `Retry-After`.** When a server returns 429 it usually states in a
  header how long to wait. Respecting it is the difference between a polite
  client and a blocked one.
- **`timeout` is mandatory.** Without it `requests` can wait indefinitely and
  silently hang a scheduled overnight run.

### 3. `src/monitor/sources/ecb.py` — first data source

https://data-api.ecb.europa.eu/service/data/%7Bflow%7D/%7Bkey%7D?format=csvdata


On the ECB portal a series is written `EXR.D.USD.EUR.SP00.A`, where `EXR` is
the *dataflow* and `D.USD.EUR.SP00.A` is the *series key* — they go in
different parts of the URL. Optional `startPeriod` / `endPeriod` parameters
restrict the range.

The response columns are validated before use:

```python
expected = {"TIME_PERIOD", "OBS_VALUE"}
missing = expected - set(raw.columns)
if missing:
    raise ValueError(...)
```

This is the same discipline as `stopifnot()`: if the API ever changes its
response shape, the script fails with a clear message instead of silently
returning an empty table.

Output contract, the same for every source: columns `date`, `value`,
`series_key`.

### 4. `scripts/demo_ecb.py` — smoke test

Acceptance test passed: 706 rows, 2024-01-02 to 2026-10-06, EUR/USD values
in the expected 1.0–1.2 range, weekdays only.

---

## Problems encountered

### Problem 1 — `pip install -e .` run from the wrong directory

ERROR: file:///C:/Users/farza does not appear to be a Python project


The terminal was in the home directory, not the project. Fixed with `cd`.

This is exactly the failure mode the phase 0 log warned about: **run `pwd`
before any command that creates files or acts on the current directory.**

### Problem 2 — `scripts/` created inside `src/`

`find . -name "*.py" -not -path "./.venv/*"` revealed the script at
`./src/scripts/demo_ecb.py` instead of `./scripts/demo_ecb.py`.

```bash
mkdir -p scripts
mv src/scripts/demo_ecb.py scripts/
rmdir src/scripts
```

Not merely cosmetic: `pyproject.toml` declares `where = ["src"]`, so anything
under `src/` is treated as part of the installable package. Development
scripts are tooling, not library code, and the separation keeps that boundary.

`find` with `-not -path "./.venv/*"` is the quick way to see the real project
structure without the noise of the virtual environment.

### Problem 3 — `ModuleNotFoundError: No module named 'monitor'`

The virtual environment was not active in that terminal, so the system Python
ran instead — and it has no `monitor` installed.

```bash
source .venv/Scripts/activate
python -c "import sys; print(sys.prefix)"   # must point inside the project
```

**A new terminal does not activate the virtual environment by itself.** Either
activate it each time, or configure the editor to select the project
interpreter automatically (VS Code: `Ctrl+Shift+P` → `Python: Select
Interpreter`).

Diagnostic tip: `(.venv)` appearing in the prompt is the quickest check.

### Problem 4 — `.egg-info` kept appearing in `git status`

`pip install -e .` generates `src/euro_area_macro_monitor.egg-info/`, package
metadata that is regenerated on any machine and must not be committed.

The root cause turned out to be two typos in `.gitignore`: `egg_info` with an
underscore instead of a hyphen, and `.pythest_cache/` instead of
`.pytest_cache/`.

```bash
sed -i 's|egg_info|egg-info|; s|pythest|pytest|' .gitignore
```

**`.gitignore` is completely silent about typos.** A pattern matching nothing
raises no error — it simply has no effect. The diagnostic tool is:

```bash
git check-ignore -v path/to/thing
```

It reports which line of `.gitignore` is responsible for ignoring a path. No
output means no pattern matches it at all.

A related subtlety: `*.egg-info/` only matches at the repository root. Use
`**/*.egg-info/` to match at any depth.

---

## Phase 1 complete

Commit: `Add HTTP layer and ECB data source; complete phase 0 log`

New files: `pyproject.toml`, `src/monitor/http.py`,
`src/monitor/sources/ecb.py`, `scripts/demo_ecb.py`.




# Phase 2 — Remaining Data Sources

Goal: add Eurostat and FRED alongside ECB, all returning the same shape.

---

## Output contract

Every source function returns a DataFrame with the same three columns:
`date`, `value`, `series_key`. This uniformity is what makes phase 3 possible —
six series from three different APIs can be stacked into one table without
any special-casing.

---

## What was built

### Eurostat — `src/monitor/sources/eurostat.py`

```
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}
```

No API key. Filters are passed as query parameters.

The response is JSON-stat, which does not store dates as keys. Instead
`value` is a dictionary whose keys are *positions* in a dimension grid:

```python
{'47': 2.6, '48': 2.1, '49': 2.1, ...}
```

The mapping from position to date lives in a separate part of the response:

```python
time_index = data["dimension"]["time"]["category"]["index"]
# {'1997-01': 0, '1997-02': 1, ...}
```

Note the direction: it maps *date to position*, and we need the reverse.

```python
position_to_date = {position: date for date, position in time_index.items()}
```

Two details that cost time:

- The dataset had 348 periods but only 301 values. Periods with no observation
  simply do not appear in `value`, which is why the keys started at 47 rather
  than 0.
- Keys in `value` are strings (`'47'`) while values in `time_index` are integers
  (`47`), so `int(position)` is required or nothing matches.

`**filters` lets any keyword argument pass through as a query parameter, so the
same function works for any dataset with any filter combination.

### FRED — `src/monitor/sources/fred.py`

```
https://api.stlouisfed.org/fred/series/observations
```

Requires a free API key from https://fredaccount.stlouisfed.org/apikeys

Secret handling follows the same pattern as the course module on APIs:

```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("FRED_API_KEY")
```

The key lives in `.env`, which is gitignored. The code contains only the
*variable name*, never the value — which is why the file is safe to commit.
`.env.example` is committed as a template so anyone cloning the repo knows
which variable is required.

FRED writes missing observations as a single dot rather than leaving them
empty, so `pd.to_numeric(..., errors="coerce")` is needed or the column ends
up as text instead of numbers.

---

## Three APIs, three response shapes

| Source | Format | Main difficulty |
|---|---|---|
| ECB | CSV | none — read directly |
| Eurostat | JSON-stat | positional index must be reversed |
| FRED | JSON | missing values written as `.` |

This variety is representative, not contrived. Any real data project meets the
same kind of inconsistency.

---

## Problems encountered

### Problem 1 — pasting Python into the shell

```
bash: import: command not found
```

Python code belongs in a `.py` file, not at the shell prompt. The terminal only
understands shell commands (`ls`, `cd`, `git`, `python`). The word `import`
means nothing to it.

General rule for this project: files under `src/` *define* things and are never
run directly; files under `scripts/` are what you execute.

### Problem 2 — `.env` created inside `scripts/`

`load_dotenv()` looks for `.env` in the current working directory. Since
scripts are run from the project root, the file must sit next to `README.md`.

```bash
mv scripts/.env .env
```

No security exposure occurred: the `.gitignore` entry `.env` matches a file of
that name in *any* directory, so it was ignored in both locations. Verified
with `git status`.

### Non-issue — VS Code notification

> An environment file is configured but terminal environment injection is
> disabled. Enable "python.terminal.useEnvFile"...

Ignored deliberately. That setting injects variables into the VS Code terminal
only. We use `python-dotenv`, which reads `.env` from inside the code itself —
editor-independent, so it works identically on a server and in CI.

---

## Phase 2 complete

New files: `src/monitor/sources/eurostat.py`, `src/monitor/sources/fred.py`,
plus throwaway test scripts.

---

# Phase 3 — Configuration and Storage

Goal: declare what to collect in one place, fetch it all, and store it properly.

---

## What was built

### `src/monitor/config.py` — separating configuration from logic

A list of dictionaries, one per indicator, each stating its source and the
parameters that source needs. Adding a new indicator is now a matter of adding
one entry — no code changes.

Six indicators: EUR/USD, ECB policy rate, euro area HICP inflation, euro area
unemployment, US CPI, US federal funds rate.

### `src/monitor/pipeline.py` — fetch everything

`fetch_one()` dispatches on the `source` field; `fetch_all()` loops over the
config and stacks the results with `pd.concat`.

Three columns are added at this stage:

- `series_key` is **overwritten** with our own readable name (`eur_usd` rather
  than `EXR.D.USD.EUR.SP00.A`). The original API code stays in `config.py`.
- `source` and `frequency` carry metadata into the table.
- `vintage_date` records when the data was retrieved.

**Why `vintage_date` matters:** Eurostat revises published statistics. Without
this column, if the April inflation figure is corrected next month, the history
changes silently and there is no way to answer "what number was published at
the time?"

The loop wraps each fetch in `try / except` so that one failing series does not
abort the whole run — the same logic as `tryCatch` inside a loop in the course
module on scraping.

### `scripts/run_pipeline.py` — write to Parquet

Result: 8,209 rows across six series, written to
`data/processed/observations.parquet`.

File size: **64 KB**. The same data as CSV would be roughly half a megabyte —
about eight times larger. Reading it back also preserves column types, so
`date` returns as a datetime rather than a string. Both are the advantages of
columnar storage covered in the course module on large structured data.

This file **is** committed. It is incremental and compressed, and it is what
makes the repository reproducible. The DuckDB file, by contrast, will not be
committed: it is binary and rewritten on every run, so git would store a
complete new copy each time.

---

## Problems encountered

### Problem 1 — `getaddrinfo failed`, repeatedly

```
NameResolutionError: Failed to resolve 'data-api.ecb.europa.eu'
```

Not a code error — DNS resolution failing intermittently on the local network.
The evidence: a second series using the *same* domain succeeded in the same run.

No fix required. The retry layer built in phase 1 absorbed it, succeeding on
the second or third attempt. This was the first real-world confirmation that
the retry logic earns its place.

### Problem 2 — Eurostat returned 200 with zero values

```
Status: 200
Number of values: 0
```

A valid response containing nothing. Rather than guessing which filter was
wrong, the API was asked what it accepts:

```python
for dim_name in data["id"]:
    categories = data["dimension"][dim_name]["category"]["index"]
    print(f"{dim_name}: {list(categories.keys())}")
```

Output:

```
s_adj: ['NSA', 'SA', 'TC']
age:   ['TOTAL', 'Y_LT25', 'Y25-74']
unit:  ['THS_PER', 'PC_ACT']
sex:   ['T', 'M', 'F']
geo:   []          ← empty
```

Every filter was valid except `geo`. Re-querying without a geo filter listed
the available areas, revealing `EA21` — "Euro area – 21 countries (from 2026)".

**Geographic codes in official statistics are not stable.** Each change in the
composition of the euro area creates a new code. This is a strong argument for
keeping such codes in a configuration file rather than buried in code.

### Problem 3 — the two euro area aggregates do not match

Changing the inflation series to `EA21` broke it; that dataset only recognises
`EA20`. Eurostat does not update area codes across all datasets simultaneously.

So in this project:

| Series | Coverage |
|---|---|
| `hicp_euro_area` | EA20 — 20 countries |
| `unemployment_euro_area` | EA21 — 21 countries |

This does not make the data wrong, but the two series do not cover an identical
population. Recorded here deliberately rather than ignored, and it should
appear as a coverage column in the README indicator table.

### Known inconsistency — `start` has no effect on Eurostat

`fetch_dataset()` takes no `start` argument, so Eurostat series return their
full history (inflation from 2000) while ECB and FRED series respect the
requested start date (2015). More data rather than less, so harmless for now,
but worth aligning later.

---

## Phase 3 so far

| Series | Rows | Range |
|---|---|---|
| ecb_policy_rate | 4,297 | 2015-01-01 → 2026-10-06 |
| eur_usd | 3,011 | 2015-01-02 → 2026-10-06 |
| hicp_euro_area | 301 | 2000-12-01 → 2025-12-01 |
| unemployment_euro_area | 320 | 2000-01-01 → 2026-08-01 |
| us_cpi | 139 | 2015-01-01 → 2026-08-01 |
| us_fed_funds_rate | 141 | 2015-01-01 → 2026-09-01 |

Note that inflation ends in December 2025 while other series run to 2026 —
publication lag, exactly what `vintage_date` exists to document.
