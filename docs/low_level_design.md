# Low-level design: REST contracts and data flow

## Service addresses and configuration

| Block | Default local address | Configuration |
| --- | --- | --- |
| Static UI | `http://127.0.0.1:8501` | `ui/config.js` sets the browser's `apiBaseUrl` |
| FastAPI | `http://127.0.0.1:8000` | `SMART_MAINTENANCE_UI_ORIGINS` sets allowed browser origins; `SMART_MAINTENANCE_MODEL_URL` sets model URL |
| MLflow probability model | `http://127.0.0.1:5001` | Compose model service mounts `models/active`; host-process alternative uses the saved MLflow run |

All public API bodies are JSON. The UI uses only FastAPI. FastAPI alone calls MLflow. Compose maps ports to loopback; container-to-container calls use service names on the private Compose network. The API reads `models/active_release.json` on each prediction so its reported run ID and threshold match the active release. The UI configuration can change without rebuilding the API or model image.

## `POST /predict`

Request schema:

| Field | Type | Accepted range/values | Unit |
| --- | --- | --- | --- |
| `type` | string | `L`, `M`, `H` | product quality class |
| `air_temperature_k` | number | 250–350 | K |
| `process_temperature_k` | number | 250–400 | K |
| `rotational_speed_rpm` | integer | 100–5000 | rpm |
| `torque_nm` | number | 0–100 | Nm |
| `tool_wear_min` | integer | 0–300 | min |

Example request:

```json
{"type":"M","air_temperature_k":298.1,"process_temperature_k":308.6,"rotational_speed_rpm":1551,"torque_nm":42.8,"tool_wear_min":0}
```

FastAPI adds `temperature_gap_k = process_temperature_k - air_temperature_k`, rounded to one decimal place, matching both ETL implementations. The seven model fields are sent to private MLflow `POST /invocations` as `{"dataframe_records":[{...}]}`. Neither identifier nor failure-mode flags enter inference. MLflow returns `{"predictions":[[P(no failure),P(failure)]]}`. FastAPI checks that the failure probability is finite and in [0,1], then sets `alert = probability >= active threshold`.

Example HTTP 200 response (ID and latency vary):

```json
{"prediction_id":"c31d...","failure_probability":0.0117,"alert":false,"recommendation":"Continue routine checks","threshold":0.37,"model_run_id":"e5260d1c99b046f79795c53a4c392575","latency_ms":24.1,"interpretation":"AI4I record classification; not a future failure forecast"}
```

An inspection result uses `"alert":true` and `"recommendation":"Schedule an inspection"`. FastAPI/Pydantic returns HTTP 422 and field details for invalid input. Unreachable MLflow returns HTTP 503. A malformed, nonfinite, or out-of-range model score returns HTTP 502. The UI shows a readable error in these cases and does not present a fabricated prediction.

## Other FastAPI endpoints

| Method and path | Input | Output / status | Side effect |
| --- | --- | --- | --- |
| `GET /health` | none | HTTP 200: `api`, `model` (`ready` or `unavailable`), `selected_run_id` | Probes MLflow `/ping`; updates readiness gauge |
| `GET /pipeline` | none | HTTP 200: `steps` (name/status/outputs), `dvc_in_sync`, `dvc_message`, `model_run_id`, `recent_jobs` | Reads `dvc.yaml`, stage outputs, and DVC remote status |
| `POST /jobs/validate` | empty body | HTTP 200: `job_id`, `name`, timestamps, `status`, `exit_code`, `console`; HTTP 409 if already running | Executes `src/validate_data.py` with 60 s timeout; appends real result to local job log |
| `POST /feedback` | `prediction_id` (8–80 chars), optional `observed_failure` (boolean/null), optional `note` (≤300 chars) | HTTP 202: `id`, `status="pending_review"`, `message`; HTTP 422 for invalid body | Appends to local pending-review log; never trains automatically |
| `GET /metrics` | none | Prometheus text exposition | Scraped every 10 s; excluded from request-count middleware |
| `GET /docs` | none | FastAPI OpenAPI page | Read-only documentation UI |

The `GET /pipeline` stage status is an output-presence check, not proof that a stage was just rerun. The DVC remote check separately reports sync status. The UI displays the latest recorded job's actual success or error console. Job and feedback logs are Git-ignored runtime data.

## Monitoring and offline operations

Prometheus scrapes FastAPI `/metrics` and node exporter; blackbox exporter probes the MLflow and UI HTTP endpoints. Grafana's provisioned dashboard uses these series. `scripts/drift_check.py --mode observations` reads at most 500 recent successful-input records from the local observation log and requires 50 before computing PSI. `--mode demo` uses a marked, deliberately shifted validation sample. Neither calls the release gate.

`scripts/retrain_candidate.py` fits on train IDs and scores on validation IDs only. `scripts/release_gate.py review` checks split hash, feature schema, zero test rows, validation AP/recall, and a loadable model artifact. Only an explicit `promote` command switches `models/active`; `rollback` restores the prior release. The API's release ID is read from the active manifest. DVC pointers track the active and candidate model directories; MLflow stores their runs.

## Files and recovery

The Git repository holds source, DVC pointer/lock files, reports, dashboard configuration, and evidence. The VM-local DVC remote holds data/model objects; `mlflow_store/` holds the tracking DB and artifacts. Both are backed up separately on the Mac alongside a full Git bundle. `dvc pull` is required after a fresh clone before the model image can be built. See `docs/resume_after_vm_shutdown.md` for the exact restart sequence.


## Submission-hardening contract update

`POST /feedback` now requires a prediction ID present in the local observation history; unknown IDs return 404. The browser exposes a flag button only. The API supports an optional note/outcome, but no review/approve/train-from-feedback interface is claimed.

`GET /pipeline` also returns `candidate_evaluation` (validation-only metrics, lineage and importance) and `local_ci` (last completed command results, timestamps and log paths). The stage list includes metric outputs as well as DVC outputs. `ready` means output files are present; it does not mean the stage just executed. CI logs retain DVC's real skip/reuse messages.

Inference holds a shared release lock; promotion holds the exclusive lock. While the latter is held, prediction returns 503 and no score. JSONL write failures return a controlled 503; model JSON errors return 502. Pipeline report schema remains extensible. `docs/openapi.json` is exported from the running API.

The API retains the field name `failure_probability` for compatibility; UI interpretation is an uncalibrated model failure score. Global permutation importance is evaluated on validation rows only and does not imply causal attribution.
