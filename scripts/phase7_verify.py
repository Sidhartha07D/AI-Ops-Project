"""One-command acceptance check for local monitoring, drift and release controls."""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def get_json(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def main():
    health = get_json("http://127.0.0.1:8000/health")
    active = json.loads((ROOT / "models/active_release.json").read_text())
    assert health["model"] == "ready" and health["selected_run_id"] == active["run_id"]
    print(f"Serving release: PASS (rolled back to {active['version']}, {active['run_id'][:8]})")

    with urllib.request.urlopen("http://127.0.0.1:8000/metrics", timeout=10) as response:
        metrics = response.read().decode()
    assert all(name in metrics for name in ("smm_http_requests_total", "smm_predictions_total", "smm_http_request_duration_seconds", "smm_validation_jobs_total"))
    print("API Prometheus metrics: PASS (requests, predictions, latency, validation)")

    targets = get_json("http://127.0.0.1:9091/api/v1/targets?state=active")["data"]["activeTargets"]
    assert len(targets) == 4 and all(target["health"] == "up" for target in targets)
    probes = get_json("http://127.0.0.1:9091/api/v1/query?query=probe_success")["data"]["result"]
    assert len(probes) == 2 and all(item["value"][1] == "1" for item in probes)
    print("Prometheus: PASS (API and host scraped; model and UI probes successful)")

    dashboards = get_json("http://127.0.0.1:3001/api/search?query=Smart%20Maintenance")
    assert any(item["uid"] == "smart-maintenance" for item in dashboards)
    print("Grafana dashboard provisioning: PASS")

    drift = json.loads((ROOT / "reports/phase7_drift_demo.json").read_text())
    assert drift["kind"] == "deliberate_shift_demo"
    assert drift["control"]["status"] == "within_reference_range"
    assert drift["shifted"]["status"] == "drift_flagged"
    print(f"Deliberate drift demo: PASS (control PSI {drift['control']['max_psi']:.4f}; shifted torque PSI {drift['shifted']['psi_by_feature']['torque_nm']:.4f})")

    observed = json.loads((ROOT / "reports/drift_latest.json").read_text())
    assert observed["kind"] == "observed_api_inputs"
    count = observed["result"]["current_rows"]
    if count < 50:
        assert observed["result"]["status"] == "insufficient_samples"
    else:
        assert observed["result"]["status"] in {"drift_flagged", "within_reference_range"}
    print(f"Real-input drift guard: PASS ({count} samples; {observed['result']['status']})")

    events = [json.loads(line) for line in (ROOT / "reports/phase7_release_events.jsonl").read_text().splitlines()]
    assert any(e["action"] == "review" and e["decision"] == "REJECT" for e in events)
    assert any(e["action"] == "promote" for e in events)
    assert any(e["action"] == "rollback" for e in events)
    original = json.loads((ROOT / "reports/model_evaluation.json").read_text())["selected_run_id"]
    assert active["run_id"] == original
    print("Release gate: PASS (rejected weaker model; promoted approved model; rolled back to original)")


if __name__ == "__main__":
    main()
