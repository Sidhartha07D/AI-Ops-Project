"""Prepare the same AI4I rows with two local Ray workers."""

import csv
import os
from pathlib import Path

os.environ.setdefault("RAY_USAGE_STATS_ENABLED", "0")
import ray

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/ai4i2020.csv"
OUTPUT = ROOT / "data/processed/ray_features.csv"
FIELDS = [
    "udi",
    "type",
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "temperature_gap_k",
    "machine_failure",
]


@ray.remote(num_cpus=1)
def prepare_batch(batch: list[dict[str, str]]) -> list[dict]:
    result = []
    for row in batch:
        air = float(row["Air temperature [K]"])
        process = float(row["Process temperature [K]"])
        result.append(
            {
                "udi": int(row["UDI"]),
                "type": row["Type"],
                "air_temperature_k": air,
                "process_temperature_k": process,
                "rotational_speed_rpm": int(row["Rotational speed [rpm]"]),
                "torque_nm": float(row["Torque [Nm]"]),
                "tool_wear_min": int(row["Tool wear [min]"]),
                "temperature_gap_k": round(process - air, 1),
                "machine_failure": int(row["Machine failure"]),
            }
        )
    return result


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 10_000
    ray.init(
        num_cpus=2,
        include_dashboard=False,
        object_store_memory=80 * 1024 * 1024,
        _memory=512 * 1024 * 1024,
        log_to_driver=False,
    )
    try:
        batches = [rows[i : i + 1000] for i in range(0, len(rows), 1000)]
        references = [prepare_batch.remote(batch) for batch in batches]
        prepared = [row for batch in ray.get(references) for row in batch]
        prepared.sort(key=lambda row: row["udi"])
        assert len(prepared) == 10_000
        assert sum(row["machine_failure"] for row in prepared) == 339
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(prepared)
        print(f"Ray version: {ray.__version__} | CPU workers: 2")
        print(f"Prepared rows: {len(prepared)} | batches: {len(batches)}")
        print(f"Output: {OUTPUT}")
        print("Ray preparation: PASS")
    finally:
        ray.shutdown()


if __name__ == "__main__":
    main()
