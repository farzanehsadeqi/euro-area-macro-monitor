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
└── requirements.lock.txt
```

Phase 0 complete: one local commit, repository size 1.45 KiB.

---

## Next steps

1. Create the GitHub repository — **without** a README, `.gitignore`, or licence,
   since the local repo already has them and git would otherwise report a conflict
   on the first push.
2. ```bash
   git remote add origin https://github.com/USERNAME/euro-area-macro-monitor.git
   git branch -M main
   git push -u origin main
   ```
3. Phase 1: first API connection (ECB, no key required) — one indicator, one
   DataFrame. Acceptance test: a table with a date column and a value column is
   returned.
