"""Archive actual local check results for submission review, without inventing cases."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ci = json.loads((ROOT / "reports/local_ci_latest.json").read_text())
    unit = json.loads((ROOT / "reports/unit_test_results.json").read_text())
    load = json.loads((ROOT / "reports/contract_load_latest.json").read_text())
    candidate = json.loads((ROOT / "reports/pipeline_evaluation.json").read_text())
    target = ROOT / "evidence/verification" / ci["git_sha"][:8]
    target.mkdir(parents=True, exist_ok=True)
    for name in [
        "local_ci_latest.json",
        "unit_test_results.json",
        "contract_load_latest.json",
        "drift_latest.json",
        "live_recovery_check.json",
    ]:
        shutil.copy2(ROOT / "reports" / name, target / name)
    shutil.copytree(
        ROOT / "reports/local_ci_logs",
        target / "logs",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".lock"),
    )
    stages = "\n".join(
        f"| {s['name']} | {s['exit_code']} | {s['seconds']} |" for s in ci["stages"]
    )
    body = f"""# Current submission verification

Observed archive date: {datetime.now(timezone.utc).isoformat()}.
Verified source commit: `{ci["git_sha"]}`. Execution: Ubuntu ARM64 VM, local CI.
This record supersedes broad completion statements in `reports/final_acceptance.md`; older phase reports remain historical.

## Actual counts

- Collected unit tests: **{unit["executed"]} executed, {unit["passed"]} passed, {unit["failures"]} failures, {unit["errors"]} errors, {unit["skipped"]} skipped**.
- Local CI commands: **{len(ci["stages"])}**, overall status **{ci["status"]}**. These commands are not additional unit test cases.
- Live integration: health, ordinary and inspection predictions, invalid input, pipeline/DVC, validation console, known prediction feedback and separate UI pages passed in the integration log.
- Direct local model/API parity: 40 requests at concurrency 2, tolerance 1e-6, {load["errors"]} errors.
- Short probe: {load["requests_per_second"]:.2f} requests/s; p50 {load["p50_ms"]:.2f} ms; p95 {load["p95_ms"]:.2f} ms. This is a short repeated-demo-input probe, not the blueprint's two-minute SLA benchmark.
- Candidate source SHA: `{candidate["git_sha"]}`; MLflow run `{candidate["run_id"]}`; train rows 6000, validation rows 2000, locked-test rows scored 0.
- Validation AP {candidate["validation_average_precision"]:.4f}; a deterministic reproduction, not a claimed improvement. Permutation importance is in the evaluation JSON and MLflow artifact, subject to correlated-feature limitations.

## Local command results

| Command | Exit code | Seconds |
| --- | ---: | ---: |
{stages}

The exact logs and JSON results are archived under `{target.relative_to(ROOT)}`. DVC reuse is shown in the pipeline log; skipped cached stages are not new training runs. The MLproject validate entry point was separately executed with its declared environment-version check in run `568a4402193344c3999f618c91191b23`.

Additional later workload and restore evidence is recorded separately in `reports/finishing_checks.md` and its linked JSON reports; each measurement identifies its own source commit.

## Release verification

`reports/live_recovery_check.json` records a deliberately injected exception after a real candidate server startup. The recovery path restarted the original model and restored both bytes and policy; post-recovery integration passed. Successful live promotion of a validation-only candidate and rollback to the original selected run were also executed. Saved events distinguish this from the operations script's history assertions. Corrupt artifact digest and forged metric fixtures were rejected on actual model evaluation.

Subsequent full Ubuntu reboot verification is recorded in `reports/vm_reboot_check.json`: boot ID changed, model bytes/policy persisted, services restarted, integration passed, DVC synced, timer active and MLflow database valid. Genuine browser outage/recovery and saved-results captures are indexed as 31–33.

## Corrections and limits

- Mislabelled image 26 was removed: it showed CI terminal output, not the outage UI. Genuine replacement browser outage/recovery captures 31/32 are now indexed, together with local-results capture 33.
- Local CI is the primary path. Historical GitHub-hosted CI is preserved; its automatic triggers are disabled. No professor exception to the cloud rule is assumed.
- MLproject declares the version snapshot; 163 installed pip package versions and Python were checked. A fresh environment installation/image digest lock was not demonstrated during this run.
- The user-level five-minute timer refreshes input drift while the user manager runs. Recent inputs include repeated course-demo requests, not new industrial measurements; no fresh-label accuracy/concept-drift claim is made.
- Release switching has intentional downtime. If automatic recovery itself fails, an explicit operator error is raised; zero-downtime or multi-host atomic deployment is not claimed.
- Role accounts, fleet replay, feedback approval/retraining from new labels, Kubernetes/KServe, Airflow, production authentication/TLS and full offline image distribution remain outside the approved reduced scope.
- Original MLflow history contains test AP in failed packaging run `4c30b295721c4cb6bb6d2b4cd67c9f95` and successful selected run `e5260d1c99b046f79795c53a4c392575`, both 0.8066445779. A strict single-evaluation claim is unsupported.
- The original selected model's uncommitted-source history remains disclosed. New clean candidate lineage does not alter that history. No frozen-test reevaluation was performed.
- AI disclosure is deferred by the user's instruction. Personal viva readiness and submission access/format need final user review.

Acceptance: the implemented local workflow passed its recorded checks. This does not certify every original blueprint feature or guarantee marks.
"""
    (ROOT / "reports/submission_acceptance.md").write_text(body)
    print("Archived actual verification:", target)


if __name__ == "__main__":
    main()
