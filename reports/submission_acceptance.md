# Current submission verification

Observed archive date: 2026-11-08T11:27:58.780693+00:00.
Verified source commit: `17aa0b4e21b0b2806542abf8f32456d65a625e81`. Execution: Ubuntu ARM64 VM, local CI.
This record supersedes broad completion statements in `reports/final_acceptance.md`; older phase reports remain historical.

## Actual counts

- Collected unit tests: **13 executed, 13 passed, 0 failures, 0 errors, 0 skipped**.
- Local CI commands: **13**, overall status **passed**. These commands are not additional unit test cases.
- Live integration: health, ordinary and inspection predictions, invalid input, pipeline/DVC, validation console, known prediction feedback and separate UI pages passed in the integration log.
- Direct local model/API parity: 40 requests at concurrency 2, tolerance 1e-6, 0 errors.
- Short probe: 44.49 requests/s; p50 41.87 ms; p95 57.15 ms. This is a short repeated-demo-input probe, not the blueprint's two-minute SLA benchmark.
- Candidate source SHA: `07c89c541e74d6fe4fd6e79fc5b4fdc01d116185`; MLflow run `f3f3943f9e544acc987012bec9ff0cda`; train rows 6000, validation rows 2000, locked-test rows scored 0.
- Validation AP 0.7495; a deterministic reproduction, not a claimed improvement. Permutation importance is in the evaluation JSON and MLflow artifact, subject to correlated-feature limitations.

## Local command results

| Command | Exit code | Seconds |
| --- | ---: | ---: |
| python_format | 0 | 0.028 |
| python_lint | 0 | 0.025 |
| environment | 0 | 0.194 |
| compile | 0 | 0.036 |
| unit_tests | 0 | 4.39 |
| dvc_pipeline | 0 | 0.754 |
| artifact_backup | 0 | 0.423 |
| feature_parity | 0 | 0.067 |
| compose_config | 0 | 0.176 |
| integration | 0 | 0.928 |
| model_contract_and_load | 0 | 4.647 |
| fresh_drift | 0 | 0.086 |
| operations | 0 | 0.255 |

The exact logs and JSON results are archived under `evidence/verification/17aa0b4e`. DVC reuse is shown in the pipeline log; skipped cached stages are not new training runs. The MLproject validate entry point was separately executed with its declared environment-version check in run `568a4402193344c3999f618c91191b23`.

## Release verification

`reports/live_recovery_check.json` records a deliberately injected exception after a real candidate server startup. The recovery path restarted the original model and restored both bytes and policy; post-recovery integration passed. Successful live promotion of a validation-only candidate and rollback to the original selected run were also executed. Saved events distinguish this from the operations script's history assertions. Corrupt artifact digest and forged metric fixtures were rejected on actual model evaluation.

## Corrections and limits

- Mislabelled image 26 was removed: it showed CI terminal output, not the outage UI. A genuine browser outage screenshot remains pending; no replacement is claimed.
- Local CI is the primary path. Historical GitHub-hosted CI is preserved; its automatic triggers are disabled. No professor exception to the cloud rule is assumed.
- MLproject declares the version snapshot; 163 installed pip package versions and Python were checked. A fresh environment installation/image digest lock was not demonstrated during this run.
- The user-level five-minute timer refreshes input drift while the user manager runs. Recent inputs include repeated course-demo requests, not new industrial measurements; no fresh-label accuracy/concept-drift claim is made.
- Release switching has intentional downtime. If automatic recovery itself fails, an explicit operator error is raised; zero-downtime or multi-host atomic deployment is not claimed.
- Role accounts, fleet replay, feedback approval/retraining from new labels, Kubernetes/KServe, Airflow, production authentication/TLS and full offline image distribution remain outside the approved reduced scope.
- Original MLflow history contains test AP in failed packaging run `4c30b295721c4cb6bb6d2b4cd67c9f95` and successful selected run `e5260d1c99b046f79795c53a4c392575`, both 0.8066445779. A strict single-evaluation claim is unsupported.
- The original selected model's uncommitted-source history remains disclosed. New clean candidate lineage does not alter that history. No frozen-test reevaluation was performed.
- AI disclosure is deferred by the user's instruction. Personal viva readiness and submission access/format need final user review.

Acceptance: the implemented local workflow passed its recorded checks. This does not certify every original blueprint feature or guarantee marks.
