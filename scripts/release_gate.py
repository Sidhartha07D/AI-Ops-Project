"""Review validation-only candidates and switch the local serving artifact.

Promotion requires a human command; drift detection never calls this script.
"""

import argparse
import json
import shutil
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
ACTIVE = MODELS / "active"
RELEASE = MODELS / "active_release.json"
PREVIOUS = MODELS / "previous_release.json"
EVENTS = ROOT / "reports/phase7_release_events.jsonl"
BASELINE = json.loads((ROOT / "reports/model_evaluation.json").read_text())


def event(action, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "action": action, **fields}, sort_keys=True) + "\n")


def write_release(release):
    RELEASE.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")


def replace_active(source):
    source = ROOT / source
    assert source.is_dir() and (source / "MLmodel").exists()
    ACTIVE.mkdir(exist_ok=True)
    for entry in ACTIVE.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()
    shutil.copytree(source, ACTIVE, dirs_exist_ok=True)


def restart_and_check():
    subprocess.run(["docker", "compose", "restart", "model"], cwd=ROOT, check=True)
    for _ in range(45):
        try:
            with urllib.request.urlopen("http://127.0.0.1:5001/ping", timeout=2) as res:
                if res.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Model did not become healthy after release switch")


def candidate(name):
    path = ROOT / "reports/retrain_candidates" / f"{name}.json"
    return json.loads(path.read_text())


def review(item):
    reasons = []
    if item["split_manifest_sha256"] != BASELINE["split_manifest_sha256"]:
        reasons.append("split manifest changed")
    if item["feature_columns"] != BASELINE["feature_columns"]:
        reasons.append("feature schema changed")
    if item["test_rows_used"] != 0:
        reasons.append("locked test was used")
    if item["validation_average_precision"] + 1e-9 < BASELINE["selected_validation"]["average_precision"]:
        reasons.append("validation average precision below champion")
    if item["validation_recall_at_champion_threshold"] + 1e-9 < BASELINE["selected_validation"]["recall"]:
        reasons.append("validation recall below champion")
    if not (ROOT / item["model_path"] / "MLmodel").exists():
        reasons.append("loadable model artifact missing")
    return reasons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "review", "promote", "rollback"])
    parser.add_argument("name", nargs="?")
    args = parser.parse_args()
    if args.action == "init":
        if RELEASE.exists():
            raise SystemExit("Release already initialized")
        replace_active("models/serving_model")
        release = {"version": "v1", "run_id": BASELINE["selected_run_id"], "model_path": "models/serving_model", "threshold": BASELINE["selected_threshold"], "validation_average_precision": BASELINE["selected_validation"]["average_precision"]}
        write_release(release)
        event("initialize", release=release)
        print("Initialized champion release v1")
        return
    if args.action in ("review", "promote"):
        if not args.name:
            parser.error("candidate name required")
        item = candidate(args.name)
        reasons = review(item)
        decision = "REJECT" if reasons else "APPROVE"
        event("review", candidate=args.name, decision=decision, reasons=reasons, run_id=item["run_id"])
        print(f"{decision}: {args.name}; reasons: {reasons or ['passed validation gate']}")
        if args.action == "review" or reasons:
            if args.action == "promote" and reasons:
                raise SystemExit(2)
            return
        previous = json.loads(RELEASE.read_text())
        PREVIOUS.write_text(json.dumps(previous, indent=2, sort_keys=True) + "\n")
        replace_active(item["model_path"])
        release = {"version": "v2", "run_id": item["run_id"], "model_path": item["model_path"], "threshold": item["threshold"], "validation_average_precision": item["validation_average_precision"]}
        write_release(release)
        restart_and_check()
        event("promote", release=release, previous=previous)
        print(f"PROMOTED: {release['run_id']}; model endpoint healthy")
        return
    if not PREVIOUS.exists():
        raise SystemExit("No previous release recorded")
    previous = json.loads(PREVIOUS.read_text())
    outgoing = json.loads(RELEASE.read_text())
    replace_active(previous["model_path"])
    write_release(previous)
    restart_and_check()
    event("rollback", release=previous, outgoing=outgoing)
    print(f"ROLLED BACK: {previous['run_id']}; model endpoint healthy")


if __name__ == "__main__":
    main()
