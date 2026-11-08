> Superseded for current submission by `reports/submission_acceptance.md`. This is a historical Phase 8 record. Audit correction: file 26 contained CI terminal output, was removed during evidence cleanup, and is not browser outage proof.

# Phase 8 acceptance record (in progress)

Observed on 2026-11-08 in the Ubuntu 26.04 ARM64 UTM VM, 4 vCPUs and 3.3 GiB RAM. `docs/test_plan.md` defines the expected outcomes. The source checkout began at Phase 7 commit `9897e61`; Phase 8 implementation checkpoint `1ea8880` added the five course documents, configurable UI API address, improved API error handling, and full data CI steps. The selected released model remains MLflow run `e5260d1c99b046f79795c53a4c392575` at threshold 0.37.

| Case | Observed result | Status |
| --- | --- | --- |
| T01 source | `src/validate_data.py` reported 10,000 rows, 339 positive labels, zero blanks, and pinned SHA-256 `dc6630cd...`; the official UCI ZIP download and extracted CSV hashes were both verified | Pass |
| T02 DVC | Four-stage DAG shown; `dvc repro --force` completed Spark, Ray, comparison and split creation; `dvc status -c` reported cache and remote in sync | Pass |
| T03 ETL | Both implementations returned 10,000 rows and feature comparison passed. Recorded earlier wall times were Spark 7.62 s/1,312 rows/s and Ray 4.37 s/2,288 rows/s (`reports/etl_benchmark.md`) | Pass |
| T04 MLflow | Selected run, metrics, tags and confusion artifact observed in prior Ubuntu Firefox screenshots 09–11; current release manifest still identifies that run. Validation-only run from clean commit is visible in screenshot 25 | Pass |
| T05 unit | Six focused API tests passed on the VM and in a fresh checkout. The final seven-test suite also rejects nonfinite sensor input and passed on the VM | Pass |
| T06 integration | Seven Compose services started; model, API and UI reported healthy. `scripts/phase5_smoke.py` passed predictions, HTTP 422, DVC status, validation, feedback and separate UI. A temporary validation-fixture bug was found during cleanup, fixed, and the smoke run passed again. Stopping the real model yielded API model-unavailable health, HTTP 503 instead of a score, and a visible UI warning (historical observation; screenshot 26 was miscaptured and removed); restarting the model restored the smoke test | Pass |
| T07 UI | Prior browser captures show routine and inspection outcomes. A 390 × 844 Firefox responsive view showed header, guidance, service readiness and form without horizontal clipping (screenshot 23). Torque 200 was blocked by the browser's 100 Nm maximum with a visible warning (screenshot 24) | Pass |
| T08 pipeline | Ubuntu Firefox showed four ready stages and DVC in sync. A separate invalid CSV fixture caused a real validation error and traceback, captured in screenshot 22; after removing the fixture, validation and smoke checks passed | Pass |
| T09 API | Earlier FastAPI docs screenshot 15 and live smoke HTTP 422 response verified. A current docs review remains | Pass for endpoint behavior |
| T10 monitoring | `scripts/phase7_verify.py` confirmed API metrics, four healthy Prometheus targets, two successful model/UI probes, and Grafana dashboard provisioning; browser captures 18, 19 and 21 show live panels | Pass |
| T11 drift and release | Phase 7 verification confirmed marked deliberate shift, eight real observations below the 50-sample minimum, a rejected candidate, approved promotion, and rollback to the original run | Pass |
| T12 restore | The VM was started again this session and Compose plus smoke checks passed. A fresh clone restored 19 DVC files and passed data checks. Separately, a disposable restore from the **Mac Phase 8 Git bundle and state archive** fetched the same 19 files, validated the source and Spark/Ray equality, found the active model, verified DVC sync, and opened the restored MLflow database with 15 runs | Pass |
| T13 CI | The workflow commands passed end-to-end in a fresh VM clone. After creating the private `Sidhartha07D/AI-Ops-Project` repository, hosted GitHub Actions run `42454769012` on commit `e757116` passed all steps: compile, unit tests, DAG, pinned UCI download, validation, forced DVC repro, Spark/Ray equality, and Compose syntax (screenshot 27) | Pass |
| T14 docs/evidence | Architecture, HLD, LLD, test plan and user manual exist. The historical index contained 24 captures through 28; the corrected current index removes redundant and mislabelled captures; viva notes are in `docs/viva_guide.md`. Evidence audit found no missing or unindexed files. Final personal viva preparation remains | Pass for documents/evidence; viva is separate |

## Defects and resolution

1. The first forced DVC run from an SSH shell failed because `python` was absent from `PATH`; rerunning with the project environment on `PATH` completed all stages. The hosted workflow uses `setup-python` and supplies `python`.
2. The error demonstration set `SMART_MAINTENANCE_VALIDATION_DATA` to a disposable invalid CSV. After Compose cleared it to an empty value, the first validator implementation treated `.` as a file and failed. The fallback now uses the pinned CSV when the setting is empty. The subsequent validation and integration smoke passed. The disposable fixture was removed; the failed job remains only in the Git-ignored job log and screenshot.
3. A smoke test attempted immediately after `docker compose restart api` met a connection reset while the API was starting. After the API reached healthy status, the unchanged smoke test passed. Operators should wait for healthy status before invoking the smoke script.

The 2026-11-08 DVC rerun reproduced the existing fixed split hash `7a1fdd0c...`; no locked-test reevaluation was performed. The original selected model run began while its training script was uncommitted, as disclosed in `docs/model_card.md`. A later commit cannot rewrite that history; provenance should be described honestly in the presentation.

At clean commit `91f9214f884fe9c2ad665c759d62abe8b4924b7b`, `mlflow run . -e validate` finished successfully as run `71c564ba12294121ab1e4f78e8eeab9e`. Its `mlflow.source.git.commit` tag exactly matches that commit. This run only revalidated the pinned CSV; it did not train, select, or evaluate the locked test set.

## Backup checkpoint

The Mac workspace stores `outputs/backups/smart-maintenance-phase8.bundle` (complete Git history through `387e843`) and `outputs/backups/smart-maintenance-phase8-state.tar.gz` (MLflow store, DVC remote and local DVC configuration). SHA-256 values are `86bfd4a0d50b55fa29fd872aa82e95e4b61b1a57170e2f1954a0e2b1bf11b4c7` and `5247fef799e9010abf7f4dc4ee6e612436084f4718f53f9aa80c3ce453d0680a`. `git bundle verify` reported a complete history. The archive and bundle were copied back into a disposable VM directory and restored; that test passed as described in T12. The temporary restore directories were removed afterward.

Hosted CI proof: `https://github.com/Sidhartha07D/AI-Ops-Project/actions/runs/42454769012`. The repository is private; a reviewer needs access to open the URL. The first hosted run on `4b9c289` also passed, but GitHub emitted deprecation notices for older action versions. Commit `e757116` moved to supported Node 24 actions and a fixed Ubuntu 24.04 runner, and the clean rerun passed.
