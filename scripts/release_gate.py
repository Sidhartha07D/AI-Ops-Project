"""Review validation-only candidates and switch the local serving artifact.

Promotion requires a human command; drift detection never calls this script.
"""

import argparse
import fcntl
import os
import sys
from tempfile import TemporaryDirectory
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
sys.path.insert(0, str(ROOT))
from scripts.artifacts import load_model, tree_digest

BASELINE = json.loads((ROOT / "reports/model_evaluation.json").read_text())


def event(action, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "action": action, **fields}, sort_keys=True) + "\n")


def write_release(release):
    temporary = RELEASE.with_suffix(".tmp")
    temporary.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, RELEASE)


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
    """Recreate the mount, then compare served outputs with the active local bundle."""
    import numpy as np
    import pandas as pd
    sample = [{"type": "M", "air_temperature_k": 298.1, "process_temperature_k": 308.6, "rotational_speed_rpm": 1551, "torque_nm": 42.8, "tool_wear_min": 0, "temperature_gap_k": 10.5}]
    expected = np.asarray(load_model(ACTIVE).predict(pd.DataFrame(sample)))
    subprocess.run(["docker", "compose", "up", "-d", "--no-deps", "--force-recreate", "model"], cwd=ROOT, check=True)
    for _ in range(45):
        try:
            request = urllib.request.Request("http://127.0.0.1:5001/invocations", data=json.dumps({"dataframe_records": sample}).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=3) as res:
                actual = np.asarray(json.load(res)["predictions"])
            if actual.shape == expected.shape and np.allclose(actual, expected, atol=1e-8):
                return
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(1)
    raise RuntimeError("Served model did not match the staged bundle")


def switch_release(release):
    """Block predictions; restore bytes and policy automatically on any failed switch."""
    source = ROOT / release["model_path"]
    load_model(source)  # Reject corrupt bundles before touching the serving release.
    with (MODELS / ".release.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        old = json.loads(RELEASE.read_text())
        with TemporaryDirectory(prefix="release-backup-", dir=MODELS) as temporary:
            backup = Path(temporary) / "model"
            shutil.copytree(ACTIVE, backup)
            try:
                subprocess.run(["docker", "compose", "stop", "model"], cwd=ROOT, check=True)
                replace_active(release["model_path"])
                restart_and_check()
                write_release({**release, "artifact_sha256": tree_digest(ACTIVE)})
            except BaseException:
                # Keep the exclusive lock while recovering, so no mixed model/policy is served.
                subprocess.run(["docker", "compose", "stop", "model"], cwd=ROOT, check=True)
                replace_active(backup)
                write_release(old)
                try:
                    restart_and_check()
                except Exception as recovery_error:
                    event("recovery_failed", error=type(recovery_error).__name__)
                    raise RuntimeError("Release failed and recovery needs operator attention") from recovery_error
                event("failed_switch_restored", release=old)
                raise
        return old


def candidate(name):
    path = ROOT / "reports/pipeline_evaluation.json" if name == "pipeline" else ROOT / "reports/retrain_candidates" / f"{name}.json"
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
    try:
        import pandas as pd
        import numpy as np
        from hashlib import sha256
        from sklearn.metrics import average_precision_score, recall_score
        from src.train_models import FEATURES
        split_path = ROOT / "data/splits/split_ids.csv"
        if sha256(split_path.read_bytes()).hexdigest() != item["split_manifest_sha256"]:
            reasons.append("actual split hash changed")
        path = ROOT / item["model_path"]
        if item.get("artifact_sha256") and tree_digest(path) != item["artifact_sha256"]:
            reasons.append("artifact digest mismatch")
        model = load_model(path)
        frame = pd.read_csv(ROOT / "data/processed/spark_features.csv").merge(pd.read_csv(split_path), on="udi", validate="one_to_one")
        validation = frame.loc[frame.split == "validation"]
        assert len(validation) == 2000
        scores = np.asarray(model.predict(validation[FEATURES]))[:, 1]
        assert np.isfinite(scores).all(), "Nonfinite artifact output"
        for key in ["threshold", "validation_average_precision", "validation_recall_at_champion_threshold"]:
            assert np.isfinite(item[key]), "Nonfinite candidate report"
        assert 0 <= item["threshold"] <= 1
        actual_ap = float(average_precision_score(validation.machine_failure, scores))
        actual_recall = float(recall_score(validation.machine_failure, scores >= item["threshold"]))
        if abs(actual_ap - item["validation_average_precision"]) > 1e-8 or abs(actual_recall - item["validation_recall_at_champion_threshold"]) > 1e-8:
            reasons.append("reported scores do not match actual artifact")
    except Exception as exc:
        reasons.append("artifact validation failed: " + type(exc).__name__)
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

        release = {"version": "v2", "run_id": item["run_id"], "model_path": item["model_path"], "threshold": item["threshold"], "validation_average_precision": item["validation_average_precision"]}
        previous = switch_release(release)
        PREVIOUS.write_text(json.dumps(previous, indent=2, sort_keys=True) + "\n")
        event("promote", release=release, previous=previous)
        print(f"PROMOTED: {release['run_id']}; model endpoint healthy")
        return
    if not PREVIOUS.exists():
        raise SystemExit("No previous release recorded")
    previous = json.loads(PREVIOUS.read_text())
    outgoing = json.loads(RELEASE.read_text())
    switch_release(previous)
    event("rollback", release=previous, outgoing=outgoing)
    print(f"ROLLED BACK: {previous['run_id']}; model endpoint healthy")


if __name__ == "__main__":
    main()
