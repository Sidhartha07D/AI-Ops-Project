# Phase 5 local API contract

The UI runs on `http://127.0.0.1:8501`, the FastAPI service on `http://127.0.0.1:8000`, and the MLflow probability model on `http://127.0.0.1:5001`. The API alone calls MLflow; browser users do not need to know the model's seven-column feature schema.

## `POST /predict`

Request body:

```json
{"type":"M","air_temperature_k":298.1,"process_temperature_k":308.6,"rotational_speed_rpm":1551,"torque_nm":42.8,"tool_wear_min":0}
```

`type` must be `L`, `M`, or `H`. Temperatures must be 250–350 K and 250–400 K; speed 100–5000 rpm; torque 0–100 Nm; wear 0–300 min. The API calculates `temperature_gap_k = process_temperature_k - air_temperature_k` and sends the seven prepared columns to the logged MLflow model. UDI, product ID, and failure-mode flags are never accepted as inputs.

Successful response (values vary by reading):

```json
{"prediction_id":"…","failure_probability":0.0117,"alert":false,"recommendation":"Continue routine checks","threshold":0.37,"model_run_id":"e5260d1c99b046f79795c53a4c392575","latency_ms":14.2,"interpretation":"AI4I record classification; not a future failure forecast"}
```

Invalid fields return HTTP 422 with field details. If the model service is down, the API returns HTTP 503. An invalid model response returns HTTP 502. Alert is true when probability is at least the validation-selected 0.37 threshold.

## Other endpoints

| Endpoint | Purpose | Response |
| --- | --- | --- |
| `GET /health` | Check API and MLflow service | `api`, `model`, `selected_run_id` |
| `GET /pipeline` | Read DVC stages, local remote status, latest validation jobs | `steps`, `dvc_in_sync`, `dvc_message`, `model_run_id`, `recent_jobs` |
| `POST /jobs/validate` | Run the source CSV validation script and save its real console output | Job ID, status, exit code, timestamps, console |
| `POST /feedback` | Queue user feedback for human review | HTTP 202 with `pending_review` ID; no automatic training |

The services bind to loopback and are intended for the VM demo. FastAPI's generated interface is at `http://127.0.0.1:8000/docs`. The UI is a separate static service with its own files and port. This separation also prepares the frontend and backend for independent containers in Phase 6.
