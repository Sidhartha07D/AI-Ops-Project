"""Validate the downloaded AI4I 2020 CSV with Python's standard library."""

from collections import Counter
import csv
import argparse
import json
import math
from hashlib import sha256
import os
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data/raw/ai4i2020.csv"
DATA = Path(os.environ.get("SMART_MAINTENANCE_VALIDATION_DATA") or DEFAULT_DATA)
EXPECTED = [
    "UDI", "Product ID", "Type", "Air temperature [K]",
    "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]",
    "Tool wear [min]", "Machine failure", "TWF", "HDF", "PWF",
    "OSF", "RNF",
]
NUMERIC = EXPECTED[3:8]
FLAGS = EXPECTED[9:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()
    raw = DATA.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e", "Pinned source hash mismatch"
    with DATA.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == EXPECTED, f"Unexpected columns: {reader.fieldnames}"
        rows = list(reader)
    assert len(rows) == 10_000, f"Expected 10,000 rows, got {len(rows)}"
    assert all(all(value.strip() for value in row.values()) for row in rows), "Blank cell found"
    assert len({row["UDI"] for row in rows}) == len(rows), "Duplicate UDI found"
    assert {row["Type"] for row in rows} <= {"L", "M", "H"}, "Unexpected Type"
    for row in rows:
        for column in NUMERIC:
            assert math.isfinite(float(row[column])), "Nonfinite source value"
        assert row["Machine failure"] in {"0", "1"}, "Unexpected target"
        assert all(row[column] in {"0", "1"} for column in FLAGS), "Unexpected failure flag"
    labels = Counter(row["Machine failure"] for row in rows)
    print(f"File: {DATA}")
    print(f"SHA-256: {sha256(raw).hexdigest()}")
    print(f"Rows: {len(rows)} | Columns: {len(EXPECTED)} | Blank cells: 0")
    print(f"Machine failure: 0={labels['0']}, 1={labels['1']}")
    print("Type:", dict(Counter(row["Type"] for row in rows)))
    if args.report:
        Path(args.report).write_text(json.dumps({"sha256": digest, "rows": len(rows), "status": "pass"}, indent=2) + "\n")
    print("Validation: PASS")


if __name__ == "__main__":
    main()
