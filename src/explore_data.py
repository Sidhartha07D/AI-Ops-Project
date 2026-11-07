"""Create an auditable, lightweight EDA report for the raw AI4I CSV."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/ai4i2020.csv"
REPORT = ROOT / "reports/data_audit.json"
FIGURES = ROOT / "reports/figures"
INPUTS = [
    "Type", "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
]
FLAGS = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def main() -> None:
    frame = pd.read_csv(SOURCE, encoding="utf-8-sig")
    assert len(frame) == 10_000
    mismatch = frame["Machine failure"] != frame[FLAGS].any(axis=1).astype(int)
    report = {
        "source": str(SOURCE),
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "blank_cells": int(frame.isna().sum().sum()),
        "duplicate_udi": int(frame.duplicated("UDI").sum()),
        "duplicate_input_rows": int(frame.duplicated(INPUTS).sum()),
        "machine_failure_counts": {str(k): int(v) for k, v in frame["Machine failure"].value_counts().sort_index().items()},
        "type_counts": {str(k): int(v) for k, v in frame["Type"].value_counts().sort_index().items()},
        "target_vs_failure_mode_disagreements": int(mismatch.sum()),
        "numeric_ranges": {
            column: {"min": float(frame[column].min()), "max": float(frame[column].max())}
            for column in INPUTS[1:]
        },
        "interpretation": "Synthetic observation-level failure label; no future failure horizon or real machine history.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    counts = frame["Machine failure"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.bar(["No failure", "Failure"], counts.values, color=["#377eb8", "#e6550d"])
    ax.set_ylabel("Observations")
    ax.set_title("AI4I 2020 class balance")
    for index, value in enumerate(counts.values):
        ax.text(index, value, str(value), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIGURES / "class_balance.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(11, 6.5))
    for ax, column in zip(axes.flat, INPUTS[1:]):
        for label, color in [(0, "#377eb8"), (1, "#e6550d")]:
            subset = frame.loc[frame["Machine failure"] == label, column]
            ax.hist(subset, bins=30, density=True, alpha=0.55, label=str(label), color=color)
        ax.set_title(column)
        ax.set_ylabel("Density")
    axes.flat[5].axis("off")
    axes.flat[0].legend(title="Failure")
    fig.suptitle("Sensor distributions by observed failure label")
    fig.tight_layout()
    fig.savefig(FIGURES / "sensor_distributions.png", dpi=140)
    plt.close(fig)

    print(f"Rows: {report['rows']} | blank cells: {report['blank_cells']} | duplicate inputs: {report['duplicate_input_rows']}")
    print(f"Failure labels: {report['machine_failure_counts']} | mode disagreements: {report['target_vs_failure_mode_disagreements']}")
    print(f"Report: {REPORT}")
    print("EDA: PASS")


if __name__ == "__main__":
    main()
