"""Create one chart per series and save them to output/."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # no window, just write files
import matplotlib.pyplot as plt
import pandas as pd

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_parquet("data/processed/observations.parquet")

for name, group in df.groupby("series_key"):
    group = group.sort_values("date")

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(group["date"], group["value"], linewidth=1.2, color="#1f5f5b")

    ax.set_title(name.replace("_", " "), loc="left", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{name}.png", dpi=120)
    plt.close(fig)

    print(f"Saved {name}.png  ({len(group)} points)")