# Prepared data schema

Both Spark and Ray read the DVC-tracked AI4I CSV and write the same 10,000 rows in `UDI` order. The two outputs are compared row by row before model training.

| Column | Role |
| --- | --- |
| `udi` | Audit identifier; exclude from model inputs |
| `type` | Machine product quality variant; categorical input |
| `air_temperature_k` | Numeric input |
| `process_temperature_k` | Numeric input |
| `rotational_speed_rpm` | Numeric input |
| `torque_nm` | Numeric input |
| `tool_wear_min` | Numeric input |
| `temperature_gap_k` | Derived numeric input: process minus air temperature |
| `machine_failure` | Binary target; exclude from model inputs |

The source columns `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, and `RNF` are omitted. The latter five indicate failure modes and would leak the target. The target is an observation-level failure label, not a forecast over a future time horizon.

Run `dvc repro` from the project environment to reproduce both preparation jobs, then `python src/compare_features.py` to verify equivalence. The jobs run sequentially with two workers each to fit the VM.
