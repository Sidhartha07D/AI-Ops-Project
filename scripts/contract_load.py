"""Small local model/API parity and load probe; no locked-test evaluation."""

import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.artifacts import load_model
from src.train_models import ROOT

sample = {
    "type": "M",
    "air_temperature_k": 298.1,
    "process_temperature_k": 308.6,
    "rotational_speed_rpm": 1551,
    "torque_nm": 42.8,
    "tool_wear_min": 0,
}
expected = float(
    np.asarray(
        load_model(ROOT / "models/active").predict(
            pd.DataFrame([{**sample, "temperature_gap_k": 10.5}])
        )
    )[0, 1]
)


def predict(_):
    start = time.perf_counter()
    request = urllib.request.Request(
        "http://127.0.0.1:8000/predict",
        data=json.dumps(sample).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        item = json.load(response)
    assert abs(item["failure_probability"] - expected) < 1e-6
    return (time.perf_counter() - start) * 1000


predict(0)
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=2) as pool:
    latency = list(pool.map(predict, range(40)))
elapsed = time.perf_counter() - start
report = {
    "requests": 40,
    "concurrency": 2,
    "errors": 0,
    "elapsed_seconds": elapsed,
    "requests_per_second": 40 / elapsed,
    "p50_ms": float(np.percentile(latency, 50)),
    "p95_ms": float(np.percentile(latency, 95)),
    "parity_tolerance": 1e-6,
    "interpretation": "Short closed-loop local probe, not the blueprint two-minute SLA test; repeated training-set demo input, no label scoring.",
}
(ROOT / "reports/contract_load_latest.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print(json.dumps(report, indent=2))
