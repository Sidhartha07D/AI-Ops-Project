"""Bounded paced local API measurement; repeated demo inputs, no label scoring."""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.artifacts import load_model

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = {
    "type": "M",
    "air_temperature_k": 298.1,
    "process_temperature_k": 308.6,
    "rotational_speed_rpm": 1551,
    "torque_nm": 42.8,
    "tool_wear_min": 0,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 600:
        parser.error("seconds must be between 1 and 600")
    expected = float(
        np.asarray(
            load_model(ROOT / "models/active").predict(
                pd.DataFrame([{**SAMPLE, "temperature_gap_k": 10.5}])
            )
        )[0, 1]
    )
    source = (
        __import__("subprocess")
        .check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True)
        .strip()
    )
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    deadline = start + args.seconds

    def worker(_):
        results = []
        due = start
        while time.perf_counter() < deadline:
            if time.perf_counter() < due:
                time.sleep(min(due, deadline) - time.perf_counter())
            if time.perf_counter() >= deadline:
                break
            before = time.perf_counter()
            error = None
            try:
                request = urllib.request.Request(
                    "http://127.0.0.1:8000/predict",
                    data=json.dumps(SAMPLE).encode(),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request, timeout=10) as response:
                    item = json.load(response)
                if abs(item["failure_probability"] - expected) > 1e-6:
                    error = "model/API mismatch"
            except (
                urllib.error.URLError,
                ValueError,
                KeyError,
                TypeError,
                TimeoutError,
            ) as exc:
                error = type(exc).__name__
            results.append(
                {"ms": (time.perf_counter() - before) * 1000, "error": error}
            )
            due = max(due + 1, time.perf_counter())
        return results

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [result for group in pool.map(worker, range(2)) for result in group]
    elapsed = time.perf_counter() - start
    success = [r["ms"] for r in results if r["error"] is None]
    errors = [r["error"] for r in results if r["error"] is not None]
    report = {
        "started_at": started_at,
        "git_sha": source,
        "requested_seconds": args.seconds,
        "elapsed_seconds": elapsed,
        "clients": 2,
        "maximum_offered_requests_per_second": 2,
        "requests": len(results),
        "successful_requests": len(success),
        "errors": len(errors),
        "error_types": sorted(set(errors)),
        "error_rate": len(errors) / len(results) if results else None,
        "requests_per_second": len(results) / elapsed,
        "p50_ms": float(np.percentile(success, 50)) if success else None,
        "p95_ms": float(np.percentile(success, 95)) if success else None,
        "p99_ms": float(np.percentile(success, 99)) if success else None,
        "parity_tolerance": 1e-6,
        "interpretation": "Two paced clients, at most one request per client per second. Successful-request latency includes client/network/JSON time. Repeated training demo, no label scoring. This measures this local workload, not saturation capacity or a guaranteed production SLA.",
    }
    (ROOT / "reports/sustained_load.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    return 0 if results and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
