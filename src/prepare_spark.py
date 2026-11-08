"""Prepare the AI4I rows with a small, local PySpark job."""

import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/ai4i2020.csv"
OUTPUT = ROOT / "data/processed/spark_features.csv"


def main() -> None:
    os.environ["PYSPARK_PYTHON"] = sys.executable
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("smart-maintenance-prepare")
        .config("spark.driver.memory", "1g")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        raw = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(str(SOURCE))
        )
        prepared = raw.select(
            F.col("UDI").cast("int").alias("udi"),
            F.col("Type").alias("type"),
            F.col("Air temperature [K]").cast("double").alias("air_temperature_k"),
            F.col("Process temperature [K]")
            .cast("double")
            .alias("process_temperature_k"),
            F.col("Rotational speed [rpm]").cast("int").alias("rotational_speed_rpm"),
            F.col("Torque [Nm]").cast("double").alias("torque_nm"),
            F.col("Tool wear [min]").cast("int").alias("tool_wear_min"),
            F.round(
                F.col("Process temperature [K]") - F.col("Air temperature [K]"), 1
            ).alias("temperature_gap_k"),
            F.col("Machine failure").cast("int").alias("machine_failure"),
        )
        count = prepared.count()
        assert count == 10_000, f"Expected 10,000 rows, got {count}"
        assert prepared.dropna().count() == count, "Missing prepared values"
        failures = {
            row["machine_failure"]: row["count"]
            for row in prepared.groupBy("machine_failure").count().collect()
        }
        assert failures == {0: 9661, 1: 339}, f"Unexpected labels: {failures}"
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="spark_parts_", dir=OUTPUT.parent) as temporary:
            prepared.orderBy("udi").coalesce(1).write.mode("overwrite").option(
                "header", True
            ).csv(temporary)
            part = next(Path(temporary).glob("part-*.csv"))
            shutil.copyfile(part, OUTPUT)
        print(f"Spark version: {spark.version} | master: {spark.sparkContext.master}")
        print(f"Prepared rows: {count} | failure labels: {failures}")
        print(f"Output: {OUTPUT}")
        print("Spark preparation: PASS")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
