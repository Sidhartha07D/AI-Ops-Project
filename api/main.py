"""Local API around the versioned MLflow probability model."""

from __future__ import annotations

import json
import fcntl
from contextlib import contextmanager
import logging
import math
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "reports/model_evaluation.json").read_text())
RELEASE = ROOT / "models/active_release.json"
MODEL_URL = os.environ.get(
    "SMART_MAINTENANCE_MODEL_URL", "http://127.0.0.1:5001"
).rstrip("/")
UI_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "SMART_MAINTENANCE_UI_ORIGINS", "http://127.0.0.1:8501,http://localhost:8501"
    ).split(",")
    if origin.strip()
]
PYTHON = os.environ.get(
    "SMART_MAINTENANCE_PYTHON",
    str(Path.home() / "miniconda/envs/smart-maintenance/bin/python"),
)
DVC = os.environ.get(
    "SMART_MAINTENANCE_DVC",
    str(Path.home() / "miniconda/envs/smart-maintenance/bin/dvc"),
)
JOBS = ROOT / "reports/phase5_jobs.jsonl"
FEEDBACK = ROOT / "reports/feedback_pending.jsonl"
OBSERVATIONS = ROOT / "reports/inference_observations.jsonl"
job_lock = threading.Lock()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

REQUESTS = Counter("smm_http_requests_total", "API requests", ["path", "status"])
LATENCY = Histogram(
    "smm_http_request_duration_seconds", "API request duration", ["path"]
)
PREDICTIONS = Counter(
    "smm_predictions_total", "Predictions by alert decision", ["alert"]
)
MODEL_READY = Gauge("smm_model_ready", "Last observed MLflow model readiness")
DRIFT_UPDATED = Gauge(
    "smm_drift_report_timestamp_seconds", "Last drift report file update time"
)
CI_UPDATED = Gauge(
    "smm_local_ci_timestamp_seconds", "Last completed local CI report update time"
)
DRIFT_SAMPLES = Gauge("smm_drift_samples", "Inputs in the latest drift report")
DRIFT_PSI = Gauge("smm_drift_max_psi", "Largest PSI; NaN when insufficient inputs")
VALIDATIONS = Counter(
    "smm_validation_jobs_total", "Validation job outcomes", ["status"]
)

app = FastAPI(
    title="Smart Maintenance Monitor API",
    version="0.7.0",
    description="Local course demonstration. Scores describe an AI4I 2020 record, not a future failure forecast.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=UI_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def measure_http(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled API request failure")
        from fastapi.responses import JSONResponse

        response = JSONResponse(
            status_code=503,
            content={
                "detail": "Local service error; retry later or contact the operator"
            },
        )
    path = (
        request.url.path
        if request.url.path
        in {"/health", "/predict", "/feedback", "/pipeline", "/jobs/validate"}
        else "other"
    )
    REQUESTS.labels(path=path, status=str(response.status_code)).inc()
    LATENCY.labels(path=path).observe(time.perf_counter() - start)
    return response


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    for name, timestamp_gauge in [
        ("drift_latest.json", DRIFT_UPDATED),
        ("local_ci_latest.json", CI_UPDATED),
    ]:
        path = ROOT / "reports" / name
        timestamp_gauge.set(path.stat().st_mtime if path.exists() else 0)
    path = ROOT / "reports/drift_latest.json"
    if path.exists():
        try:
            result = json.loads(path.read_text())["result"]
            DRIFT_SAMPLES.set(result["current_rows"])
            DRIFT_PSI.set(
                result["max_psi"] if result["max_psi"] is not None else float("nan")
            )
        except (OSError, ValueError, KeyError):
            logger.warning("Drift report unavailable")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class Reading(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    type: Literal["L", "M", "H"]
    air_temperature_k: float = Field(ge=250, le=350)
    process_temperature_k: float = Field(ge=250, le=400)
    rotational_speed_rpm: int = Field(ge=100, le=5000)
    torque_nm: float = Field(ge=0, le=100)
    tool_wear_min: int = Field(ge=0, le=300)


class Feedback(BaseModel):
    prediction_id: str = Field(min_length=8, max_length=80)
    observed_failure: bool | None = None
    note: str = Field(default="", max_length=300)


def fetch_model(path: str, payload: dict | None = None, timeout: float = 8) -> object:
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        MODEL_URL + path,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
        if path == "/ping":
            return {"ok": True}
        try:
            return json.loads(raw) if raw else {"ok": True}
        except ValueError as exc:
            raise HTTPException(
                status_code=502, detail="Model returned invalid JSON"
            ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.warning("Model request failed at %s: %s", path, type(exc).__name__)
        raise HTTPException(
            status_code=503, detail=f"Model service unavailable: {type(exc).__name__}"
        ) from exc


def append_jsonl(path: Path, item: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(item, sort_keys=True) + "\n")
    except OSError as exc:
        logger.exception("Local storage write failed")
        raise HTTPException(
            status_code=503, detail="Local storage unavailable; please retry later"
        ) from exc


def active_release() -> dict:
    if RELEASE.exists():
        return json.loads(RELEASE.read_text())
    return {
        "run_id": REPORT["selected_run_id"],
        "threshold": REPORT["selected_threshold"],
    }


@app.get("/health")
def health() -> dict:
    try:
        fetch_model("/ping", timeout=2)
        model = "ready"
    except HTTPException:
        model = "unavailable"
    MODEL_READY.set(1 if model == "ready" else 0)
    return {
        "api": "ready",
        "model": model,
        "selected_run_id": active_release()["run_id"],
    }


@contextmanager
def release_read_lock():
    """Exclude predictions during a release change to keep model/policy consistent."""
    with (ROOT / "models/.release.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise HTTPException(
                status_code=503, detail="Model release in progress; retry shortly"
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


@app.post("/predict")
def predict(reading: Reading) -> dict:
    with release_read_lock():
        return predict_locked(reading)


def predict_locked(reading: Reading) -> dict:
    start = time.perf_counter()
    prediction_id = uuid4().hex
    features = reading.model_dump()
    features["temperature_gap_k"] = round(
        features["process_temperature_k"] - features["air_temperature_k"], 6
    )
    result = fetch_model("/invocations", {"dataframe_records": [features]})
    try:
        probability = float(result["predictions"][0][1])
    except (TypeError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail="Model returned an invalid prediction"
        ) from exc
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        logger.error("Model returned out-of-range probability")
        raise HTTPException(
            status_code=502, detail="Model returned an invalid prediction"
        )
    release = active_release()
    threshold = float(release["threshold"])
    alert = probability >= threshold
    PREDICTIONS.labels(alert=str(alert).lower()).inc()
    append_jsonl(
        OBSERVATIONS,
        {
            "prediction_id": prediction_id,
            "model_run_id": release["run_id"],
            "received_at": datetime.now(timezone.utc).isoformat(),
            **features,
            "failure_probability": round(probability, 6),
            "alert": alert,
        },
    )
    logger.info(
        "Prediction served: release=%s alert=%s latency_ms=%.1f",
        release["run_id"][:8],
        alert,
        (time.perf_counter() - start) * 1000,
    )
    return {
        "prediction_id": prediction_id,
        "failure_probability": round(probability, 6),
        "alert": alert,
        "recommendation": "Schedule an inspection"
        if alert
        else "Continue routine checks",
        "threshold": round(threshold, 2),
        "model_run_id": release["run_id"],
        "latency_ms": round((time.perf_counter() - start) * 1000, 1),
        "interpretation": "AI4I record classification; not a future failure forecast",
    }


@app.post("/feedback", status_code=202)
def feedback(item: Feedback) -> dict:
    try:
        known = OBSERVATIONS.exists() and any(
            json.loads(line).get("prediction_id") == item.prediction_id
            for line in OBSERVATIONS.read_text().splitlines()
            if line.strip()
        )
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=503, detail="Prediction history unavailable"
        ) from exc
    if not known:
        raise HTTPException(
            status_code=404, detail="Prediction was not found in local history"
        )
    record = {
        "id": uuid4().hex,
        "received_at": datetime.now(timezone.utc).isoformat(),
        **item.model_dump(),
        "status": "pending_review",
    }
    append_jsonl(FEEDBACK, record)
    logger.info("Feedback queued: id=%s", record["id"])
    return {
        "id": record["id"],
        "status": "pending_review",
        "message": "Saved for review; it will not change the model automatically.",
    }


@app.get("/pipeline")
def pipeline() -> dict:
    config = yaml.safe_load((ROOT / "dvc.yaml").read_text())
    steps = []
    for name, stage in config["stages"].items():
        entries = stage.get("outs", []) + stage.get("metrics", [])
        outputs = [
            ROOT / (next(iter(entry)) if isinstance(entry, dict) else entry)
            for entry in entries
        ]
        steps.append(
            {
                "name": name,
                "status": "ready"
                if outputs and all(p.exists() for p in outputs)
                else "missing",
                "outputs": [str(p.relative_to(ROOT)) for p in outputs],
            }
        )
    try:
        dvc = subprocess.run(
            [DVC, "status", "-c"], cwd=ROOT, text=True, capture_output=True, timeout=20
        )
        dvc_message = (dvc.stdout + dvc.stderr).strip()
        dvc_ok = dvc.returncode == 0 and "in sync" in dvc_message
    except (OSError, subprocess.TimeoutExpired) as exc:
        dvc_message = f"Check failed: {type(exc).__name__}"
        logger.warning("DVC status check failed: %s", type(exc).__name__)
        dvc_ok = False
    jobs = []
    if JOBS.exists():
        jobs = [
            json.loads(line)
            for line in JOBS.read_text().splitlines()[-8:]
            if line.strip()
        ]
    evaluation_path = ROOT / "reports/pipeline_evaluation.json"
    evaluation = (
        json.loads(evaluation_path.read_text()) if evaluation_path.exists() else None
    )
    ci_path = ROOT / "reports/local_ci_latest.json"
    ci = json.loads(ci_path.read_text()) if ci_path.exists() else None
    return {
        "local_ci": ci,
        "candidate_evaluation": evaluation,
        "steps": steps,
        "dvc_in_sync": dvc_ok,
        "dvc_message": dvc_message,
        "model_run_id": active_release()["run_id"],
        "recent_jobs": jobs,
    }


@app.post("/jobs/validate")
def run_validation() -> dict:
    if not job_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409, detail="A validation job is already running"
        )
    started = datetime.now(timezone.utc).isoformat()
    try:
        try:
            run = subprocess.run(
                [PYTHON, "src/validate_data.py"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            output = (run.stdout + run.stderr).strip()[-3000:]
            status = "success" if run.returncode == 0 else "error"
            exit_code = run.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            output = f"{type(exc).__name__}: {exc}"
            status = "error"
            exit_code = -1
        item = {
            "job_id": uuid4().hex[:10],
            "name": "validate_data",
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "exit_code": exit_code,
            "console": output,
        }
        append_jsonl(JOBS, item)
        VALIDATIONS.labels(status=status).inc()
        logger.info(
            "Validation job %s: %s (exit %s)", item["job_id"], status, exit_code
        )
        return item
    finally:
        job_lock.release()
