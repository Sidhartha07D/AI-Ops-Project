"""Compare recent input distributions with the fixed training reference.

The demo mode deliberately shifts validation inputs; it is not production drift.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min"]
THRESHOLD = 0.2
MIN_SAMPLES = 50


def load_reference():
    with (ROOT / "data/splits/split_ids.csv").open(newline="") as file:
        split = {row["udi"]: row["split"] for row in csv.DictReader(file)}
    with (ROOT / "data/processed/spark_features.csv").open(newline="") as file:
        rows = list(csv.DictReader(file))
    return [row for row in rows if split[row["udi"]] == "train"], [row for row in rows if split[row["udi"]] == "validation"]


def psi(reference: list[float], current: list[float]) -> float:
    ordered = sorted(reference)
    cuts = sorted({ordered[int(len(ordered) * i / 10)] for i in range(1, 10)})
    bins = len(cuts) + 1
    base = [0] * bins
    recent = [0] * bins
    for value in reference:
        base[bisect.bisect_right(cuts, value)] += 1
    for value in current:
        recent[bisect.bisect_right(cuts, value)] += 1
    epsilon = 0.0001
    return sum((q - p) * math.log(q / p) for a, b in zip(base, recent)
               for p, q in [(max(a / len(reference), epsilon), max(b / len(current), epsilon))])


def compare(reference: list[dict], current: list[dict], source: str) -> dict:
    result = {"source": source, "reference_rows": len(reference), "current_rows": len(current), "threshold": THRESHOLD}
    if len(current) < MIN_SAMPLES:
        result.update(status="insufficient_samples", psi_by_feature={}, max_psi=None)
        return result
    scores = {name: round(psi([float(row[name]) for row in reference], [float(row[name]) for row in current]), 4) for name in FEATURES}
    result.update(status="drift_flagged" if max(scores.values()) > THRESHOLD else "within_reference_range", psi_by_feature=scores, max_psi=max(scores.values()))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "observations"], required=True)
    args = parser.parse_args()
    train, validation = load_reference()
    if args.mode == "demo":
        shifted = [dict(row, torque_nm=min(100.0, float(row["torque_nm"]) + 25.0)) for row in validation]
        output = {"kind": "deliberate_shift_demo", "created_at": datetime.now(timezone.utc).isoformat(), "control": compare(train, validation, "fixed_validation_inputs"), "shifted": compare(train, shifted, "fixed_validation_inputs_with_torque_plus_25_nm")}
        path = ROOT / "reports/phase7_drift_demo.json"
    else:
        path = ROOT / "reports/drift_latest.json"
        observations = ROOT / "reports/inference_observations.jsonl"
        current = [json.loads(line) for line in observations.read_text().splitlines()[-500:] if line] if observations.exists() else []
        output = {"kind": "observed_api_inputs", "created_at": datetime.now(timezone.utc).isoformat(), "result": compare(train, current, "recent_api_inputs")}
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))
    print(f"Saved: {path}")


if __name__ == "__main__":
    main()
