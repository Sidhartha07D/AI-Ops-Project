"""Check that Spark and Ray produce the same model preparation rows."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPARK = ROOT / "data/processed/spark_features.csv"
RAY = ROOT / "data/processed/ray_features.csv"
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
FLOAT_FIELDS = {
    "air_temperature_k",
    "process_temperature_k",
    "torque_nm",
    "temperature_gap_k",
}


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == FIELDS, f"Unexpected columns in {path}"
        return list(reader)


def main() -> None:
    spark_rows, ray_rows = load(SPARK), load(RAY)
    assert len(spark_rows) == len(ray_rows) == 10_000
    for index, (spark_row, ray_row) in enumerate(zip(spark_rows, ray_rows), 1):
        for field in FIELDS:
            left, right = spark_row[field], ray_row[field]
            if field in FLOAT_FIELDS:
                assert abs(float(left) - float(right)) < 1e-8, (
                    index,
                    field,
                    left,
                    right,
                )
            else:
                assert left == right, (index, field, left, right)
    print(f"Compared rows: {len(spark_rows)} | columns: {len(FIELDS)}")
    print("Identifier and failure-mode flags are not model inputs.")
    print("Spark and Ray output comparison: PASS")


if __name__ == "__main__":
    main()
