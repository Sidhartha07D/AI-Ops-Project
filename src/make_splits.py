"""Write a fixed 60/20/20, stratified ID manifest before model fitting."""

from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/spark_features.csv"
MANIFEST = ROOT / "data/splits/split_ids.csv"
REPORT = ROOT / "reports/split_summary.json"
SEED = 42


def main() -> None:
    frame = pd.read_csv(SOURCE)
    assert len(frame) == 10_000
    assert frame["udi"].is_unique, "Duplicate UDI"
    assert not frame.duplicated(
        frame.columns.drop(["udi", "machine_failure"]).tolist()
    ).any(), "Exact input duplicates require grouping"
    train_val, test = train_test_split(
        frame, test_size=0.20, random_state=SEED, stratify=frame["machine_failure"]
    )
    train, validation = train_test_split(
        train_val,
        test_size=0.25,
        random_state=SEED,
        stratify=train_val["machine_failure"],
    )
    parts = {"train": train, "validation": validation, "test": test}
    manifest = pd.concat(
        [part[["udi"]].assign(split=name) for name, part in parts.items()],
        ignore_index=True,
    ).sort_values("udi")
    assert manifest["udi"].is_unique and len(manifest) == len(frame)
    assert {name: len(part) for name, part in parts.items()} == {
        "train": 6000,
        "validation": 2000,
        "test": 2000,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(MANIFEST, index=False)
    report = {
        "seed": SEED,
        "method": "stratified random 60/20/20; exact duplicate inputs checked absent",
        "locked_test_policy": "test IDs are not used for model or threshold selection",
        "manifest_sha256": sha256(MANIFEST.read_bytes()).hexdigest(),
        "splits": {
            name: {
                "rows": int(len(part)),
                "failures": int(part["machine_failure"].sum()),
                "failure_rate": float(part["machine_failure"].mean()),
            }
            for name, part in parts.items()
        },
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Split IDs: {MANIFEST}")
    for name, info in report["splits"].items():
        print(f"{name}: {info['rows']} rows, {info['failures']} failures")
    print(f"Manifest SHA-256: {report['manifest_sha256']}")
    print("Split validation: PASS")


if __name__ == "__main__":
    main()
