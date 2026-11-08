"""Primary VM-only CI entry point: python scripts/local_ci.py [--offline-only]."""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--offline-only", action="store_true", help="Skip running-service checks"
    )
    args = parser.parse_args()
    logs = ROOT / "reports/local_ci_logs"
    logs.mkdir(exist_ok=True)
    stages = [
        (
            "python_format",
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "api",
                "src",
                "scripts",
            ],
        ),
        (
            "python_lint",
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--select",
                "E9,F63,F7,F82",
                "api",
                "src",
                "scripts",
            ],
        ),
        ("environment", [sys.executable, "scripts/verify_environment.py"]),
        (
            "compile",
            [sys.executable, "-m", "compileall", "-q", "api", "src", "scripts"],
        ),
        ("unit_tests", [sys.executable, "scripts/run_tests.py"]),
        ("dvc_pipeline", ["dvc", "repro"]),
        ("artifact_backup", ["dvc", "push"]),
        ("feature_parity", [sys.executable, "src/compare_features.py"]),
        ("compose_config", ["docker", "compose", "config", "--quiet"]),
    ]
    if not args.offline_only:
        stages += [
            ("integration", [sys.executable, "scripts/phase5_smoke.py"]),
            ("model_contract_and_load", [sys.executable, "scripts/contract_load.py"]),
            (
                "fresh_drift",
                [sys.executable, "scripts/drift_check.py", "--mode", "observations"],
            ),
            ("operations", [sys.executable, "scripts/phase7_verify.py"]),
        ]
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "execution": "local Ubuntu VM; no hosted runner",
        "stages": [],
        "status": "running",
    }
    env = dict(os.environ, SPARK_LOCAL_IP="127.0.0.1", RAY_USAGE_STATS_ENABLED="0")
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    with (logs / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for name, command in stages:
            start = time.perf_counter()
            run = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            (logs / (name + ".log")).write_text(run.stdout)
            report["stages"].append(
                {
                    "name": name,
                    "exit_code": run.returncode,
                    "seconds": round(time.perf_counter() - start, 3),
                    "log": str((logs / (name + ".log")).relative_to(ROOT)),
                }
            )
            print(name, "PASS" if run.returncode == 0 else "FAIL", flush=True)
            if run.returncode:
                print(run.stdout[-6000:])
                report["status"] = "failed"
                break
        else:
            report["status"] = "passed"
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        (ROOT / "reports/local_ci_latest.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
    sys.exit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
