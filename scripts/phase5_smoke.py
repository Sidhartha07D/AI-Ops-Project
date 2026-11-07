"""Integration smoke check for the three local Phase 5 services."""

import json
import urllib.error
import urllib.request


def call(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, json.loads(response.read()) if response.headers.get_content_type() == "application/json" else None


base = "http://127.0.0.1:8000"
status, health = call(base + "/health")
assert status == 200 and health["api"] == health["model"] == "ready"
print("API and MLflow health: PASS")

sample = {"type": "M", "air_temperature_k": 298.1, "process_temperature_k": 308.6, "rotational_speed_rpm": 1551, "torque_nm": 42.8, "tool_wear_min": 0}
status, result = call(base + "/predict", sample)
assert status == 200 and 0 <= result["failure_probability"] <= 1 and result["model_run_id"] == health["selected_run_id"]
print(f"Prediction: PASS ({result['failure_probability']:.6f}, alert={result['alert']})")

inspection = {"type": "L", "air_temperature_k": 299.0, "process_temperature_k": 310.4, "rotational_speed_rpm": 1371, "torque_nm": 53.8, "tool_wear_min": 228}
status, flagged = call(base + "/predict", inspection)
assert status == 200 and flagged["alert"] and flagged["failure_probability"] >= flagged["threshold"]
print(f"Inspection flag: PASS ({flagged['failure_probability']:.6f})")

bad = dict(sample, rotational_speed_rpm=-1)
try:
    call(base + "/predict", bad)
    raise AssertionError("Expected validation error")
except urllib.error.HTTPError as exc:
    assert exc.code == 422
print("Invalid input response: PASS (422)")

status, pipeline = call(base + "/pipeline")
assert status == 200 and pipeline["dvc_in_sync"] and len(pipeline["steps"]) >= 4
print(f"Pipeline status: PASS ({len(pipeline['steps'])} stages, DVC in sync)")

status, job = call(base + "/jobs/validate", {})
assert status == 200 and job["status"] == "success" and "Validation: PASS" in job["console"]
print("Validation job and console: PASS")

status, feedback = call(base + "/feedback", {"prediction_id": result["prediction_id"], "note": "SMOKE TEST - ignore"})
assert status == 202 and feedback["status"] == "pending_review"
print("Review queue: PASS")

with urllib.request.urlopen("http://127.0.0.1:8501/index.html", timeout=10) as res:
    html = res.read().decode()
assert "Check a machine reading" in html
with urllib.request.urlopen("http://127.0.0.1:8501/pipeline.html", timeout=10) as res:
    html = res.read().decode()
assert "Pipeline status" in html
print("Separate UI server: PASS")
