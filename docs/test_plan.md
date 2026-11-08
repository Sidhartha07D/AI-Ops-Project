# Test plan and acceptance criteria

This plan tests the actual local VM deployment. Record commands, observed results, dates, and any failures in `reports/final_acceptance.md`. A passing script alone is not evidence that the browser UI or monitoring panels are usable.

## Environment and prerequisites

- Ubuntu ARM64 UTM VM, Python environment `smart-maintenance`, Java 17, Docker Compose, and local DVC remote.
- Git checkout, DVC data/model objects, and MLflow tracking store restored from the saved checkpoint.
- Bind published services to VM loopback. Run host-process Phase 5 **or** Compose Phase 6/7, not both on the same ports.
- Keep the original train/validation/test split fixed. Demo records and error fixtures must never enter training or test evaluation.

## Cases

| ID | Action | Expected acceptance result | Evidence |
| --- | --- | --- | --- |
| T01 | Validate pinned UCI CSV and inspect DVC pointer | Schema, 10,000 rows and target checks pass; source hash matches documentation | terminal output, `data/README.md` |
| T02 | Run `dvc repro`, inspect DAG and remote | All four stages finish; DVC remote reports in sync | terminal and DVC lock |
| T03 | Run Spark/Ray comparison and benchmark | Both produce 10,000 matching feature rows; wall time and throughput are recorded, with hardware context | comparison and benchmark report |
| T04 | Inspect MLflow selected run | Parameters, metrics, tags, model and confusion artifact visible; run ID agrees with release manifest | MLflow browser and model card |
| T05 | Run seven API unit tests | All seven pass, including invalid input, nonfinite sensor values, threshold, bad model data and unavailable model | test output |
| T06 | Start Compose and run integration smoke | Model, API and UI healthy; valid inference, 422 error, feedback, pipeline and validation succeed | Compose and smoke output |
| T07 | Use the browser UI for routine and inspection examples | Correct recommendation and score visible; invalid entry displays helpful error; no broken controls at normal and narrow viewport | Ubuntu Firefox captures |
| T08 | Open pipeline page, run validation, exercise a failure | Stage status plus actual success and error console shown; page distinguishes failure from success | Ubuntu Firefox captures and job log |
| T09 | Open API docs and submit an invalid request | OpenAPI lists working endpoints; invalid field returns HTTP 422 | Ubuntu Firefox/API output |
| T10 | Open Prometheus targets and Grafana | API, model and UI probes Up; live request, latency, memory and disk panels visible | Ubuntu Firefox captures |
| T11 | Run controlled drift and release checks | Demo shift is labeled; insufficient real observations are rejected; candidate rejection, promotion and rollback verified | Phase 7 report and output |
| T12 | Stop and restart VM services, then restore a fresh clone from Git and DVC backup | Documented restart works; model and UI answer after restore | restore log and browser check |
| T13 | Run repository CI workflow | Hosted run completes unit, source, DVC repro, comparison and Compose syntax checks; record run URL/commit | GitHub Actions run or explicit limitation |
| T14 | Audit docs and evidence | Five required documents exist; screenshots are real, distinct, indexed and match the current release | document/evidence index |

## Pass rule and defect handling

The project is accepted locally when T01–T12 and T14 pass. T13 is separately reported because it depends on a remote repository and a hosted runner. Every failure is recorded with the observed output, fix, and rerun; an unexecuted case remains **not run**, never passed. Check invalid input and service outages without editing the pinned source data. The model is a synthetic-record classifier and the test does not claim a future failure forecast or field accuracy.


## Current verification commands

`python scripts/local_ci.py` is the primary VM check. `python scripts/run_tests.py` collects **11** independent unit cases and writes exact counts. Four safety cases test storage failure, unknown feedback identity, exclusive-release locking and automatic restoration of bytes/policy after a mocked restart failure. A separate executed live recovery drill is recorded in `reports/live_recovery_check.json`. The short contract/load script uses 40 repeated demo requests at concurrency 2, compares every score with the active local model at tolerance 1e-6, and reports measured percentiles; it is not the original two-minute load target. The old T01–T14 table contains acceptance groups, not a count of automated unit tests. Operations verification inspects saved release history; a new deployment is claimed only when the release commands were actually exercised.
