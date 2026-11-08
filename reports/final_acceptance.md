# Phase 8 acceptance record (in progress)

Observed on 2026-11-08 in the Ubuntu 26.04 ARM64 UTM VM, 4 vCPUs and 3.3 GiB RAM. `docs/test_plan.md` defines the expected outcomes. The source checkout began at Phase 7 commit `9897e61`; Phase 8 implementation checkpoint `1ea8880` added the five course documents, configurable UI API address, improved API error handling, and full data CI steps. The selected released model remains MLflow run `e5260d1c99b046f79795c53a4c392575` at threshold 0.37.

| Case | Observed result | Status |
| --- | --- | --- |
| T01 source | `src/validate_data.py` reported 10,000 rows, 339 positive labels, zero blanks, and pinned SHA-256 `dc6630cd...`; the official UCI ZIP download and extracted CSV hashes were both verified | Pass |
| T02 DVC | Four-stage DAG shown; `dvc repro --force` completed Spark, Ray, comparison and split creation; `dvc status -c` reported cache and remote in sync | Pass |
| T03 ETL | Both implementations returned 10,000 rows and feature comparison passed. Recorded earlier wall times were Spark 7.62 s/1,312 rows/s and Ray 4.37 s/2,288 rows/s (`reports/etl_benchmark.md`) | Pass |
| T04 MLflow | Selected run, metrics, tags and confusion artifact observed in prior Ubuntu Firefox screenshots 09–11; current release manifest still identifies that run | Pass |
| T05 unit | Six focused API tests passed on the VM and in a fresh checkout. The final seven-test suite also rejects nonfinite sensor input and passed on the VM | Pass |
| T06 integration | Seven Compose services started; model, API and UI reported healthy. `scripts/phase5_smoke.py` passed predictions, HTTP 422, DVC status, validation, feedback and separate UI. A temporary validation-fixture bug was found during cleanup, fixed, and the smoke run passed again | Pass |
| T07 UI | Prior browser captures show routine and inspection outcomes. A 390 × 844 Firefox responsive view showed header, guidance, service readiness and form without horizontal clipping (screenshot 23). Post-change input-error browser review remains | Partial |
| T08 pipeline | Ubuntu Firefox showed four ready stages and DVC in sync. A separate invalid CSV fixture caused a real validation error and traceback, captured in screenshot 22; after removing the fixture, validation and smoke checks passed | Pass |
| T09 API | Earlier FastAPI docs screenshot 15 and live smoke HTTP 422 response verified. A current docs review remains | Pass for endpoint behavior |
| T10 monitoring | `scripts/phase7_verify.py` confirmed API metrics, four healthy Prometheus targets, two successful model/UI probes, and Grafana dashboard provisioning; browser captures 18, 19 and 21 show live panels | Pass |
| T11 drift and release | Phase 7 verification confirmed marked deliberate shift, eight real observations below the 50-sample minimum, a rejected candidate, approved promotion, and rollback to the original run | Pass |
| T12 restore | A fresh clone at `/tmp/smm-restore.T5YXyL` configured the VM DVC remote, fetched 19 files, passed source and feature comparison, found the active model artifact, and reported DVC in sync. Full Mac-backup restore and VM reboot test remain | Partial |
| T13 CI | The revised workflow's commands passed end-to-end in a second fresh clone at `/tmp/smm-ci.D3zyE5`: compile, unit tests, DAG, pinned UCI download, validation, forced DVC repro, Spark/Ray equality, Compose syntax. No GitHub Actions run has occurred because this project currently has no remote | Local pass; hosted run pending |
| T14 docs/evidence | Architecture, HLD, LLD, test plan and user manual exist. Screenshot 22 added and indexed. Final evidence and viva audit remain | Partial |

## Defects and resolution

1. The first forced DVC run from an SSH shell failed because `python` was absent from `PATH`; rerunning with the project environment on `PATH` completed all stages. The hosted workflow uses `setup-python` and supplies `python`.
2. The error demonstration set `SMART_MAINTENANCE_VALIDATION_DATA` to a disposable invalid CSV. After Compose cleared it to an empty value, the first validator implementation treated `.` as a file and failed. The fallback now uses the pinned CSV when the setting is empty. The subsequent validation and integration smoke passed. The disposable fixture was removed; the failed job remains only in the Git-ignored job log and screenshot.
3. A smoke test attempted immediately after `docker compose restart api` met a connection reset while the API was starting. After the API reached healthy status, the unchanged smoke test passed. Operators should wait for healthy status before invoking the smoke script.

The 2026-11-08 DVC rerun reproduced the existing fixed split hash `7a1fdd0c...`; no locked-test reevaluation was performed. The original selected model run began while its training script was uncommitted, as disclosed in `docs/model_card.md`. A later commit cannot rewrite that history; provenance should be described honestly in the presentation.
