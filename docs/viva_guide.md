# Viva preparation: explain the working system

Use this as speaking notes, not as a script to memorize. Open the matching real page or file when asked. Do not claim field accuracy, future-failure prediction, hosted CI, or Kubernetes execution without evidence.

## Two-minute walkthrough

1. The source is UCI AI4I 2020: 10,000 **synthetic** rows, 339 machine-failure labels. The label belongs to the same row. We classify current-record failure, not time until failure.
2. Git tracks source and documents. DVC tracks the raw CSV, Spark/Ray outputs, fixed split, and model artifacts through a four-stage DAG; its actual objects live in a separate local remote.
3. Spark and Ray independently prepare the same seven modeling fields. A comparison script checks all 10,000 rows. The fixed 60/20/20 stratified split keeps validation separate from the locked test.
4. MLflow logs four candidate experiments and the chosen pipeline with parameters, metrics, tags and artifacts. The selected model is served by MLflow, wrapped by FastAPI, and used by a separate static browser UI. The released threshold is 0.37.
5. Docker Compose runs independent model, API, UI, Prometheus, exporters and Grafana services. Monitoring shows actual requests, latency, service probes, and VM resources. Drift and retraining are offline, reviewed operations with explicit promotion and rollback.

## Questions to answer precisely

| Likely question | Answer to demonstrate |
| --- | --- |
| Why not optimize accuracy? | Positive labels are only 3.39%. Predicting no failure would look accurate while missing every failure. We selected by validation average precision and chose an alert threshold with validation F2. Report precision, recall and confusion matrix too. |
| Why this dataset? | Open, small enough for the VM, has temperatures, speed, torque and wear, and permits the full local toolchain. It is synthetic and lacks a future horizon, so the model is a same-row classifier. |
| How was leakage avoided? | `UDI`/Product ID are identifiers, and TWF/HDF/PWF/OSF/RNF are failure-mode flags that reveal the outcome; none are model inputs. The split IDs were created once. Training uses train IDs, selection uses validation IDs, and the frozen test result was logged in a failed packaging run and the successful run; the same metric does not establish a single evaluation. Current candidate work uses validation only. |
| What do Spark and Ray each do? | Both parse and derive the temperature gap independently with two local workers. They run sequentially on this 3.3 GiB VM. The comparison verifies identical rows; speed here mostly includes framework startup, so it is no claim of large-scale advantage. |
| Git versus DVC versus MLflow? | Git versions code and small manifests. DVC versions data/model files and dependencies by content hash. MLflow records experiments, parameters, metrics, tags and serving artifacts. All three are needed to reproduce and explain a release. |
| What is the request path? | Browser form → FastAPI six-field JSON and validation → derived gap → MLflow `/invocations` → probability → saved threshold and recommendation → browser. API and model are separate containers. |
| What happens when a service fails? | Invalid input returns 422; unavailable model 503; malformed score 502. The UI shows the error. Prometheus probes model/UI and the API reports readiness; no fake score is emitted. |
| What does the pipeline page prove? | DVC stage output presence, remote sync, and a real validator job with exit code and console. It does not prove a new training job ran. Screenshots show both a successful and a failed validation. |
| Is drift real? | The deliberate-shift demonstration is labeled. The real-input check has fewer than 50 observations and correctly says insufficient samples. Neither result automatically retrains or promotes a model. |
| How do you deploy and roll back? | Compose starts the seven local services. A validation-only candidate is reviewed against split/schema and champion metrics; explicit promotion switches the DVC-tracked active model; rollback restores the previous release. This was observed in Phase 7. |
| What are the limitations? | Synthetic records, random row split, no future horizon, no field validation, local-only storage, and a small VM. The original selected MLflow run began while its training script was uncommitted; that provenance limitation is disclosed. |
| What happens after VM shutdown? | Git/DVC/MLflow state persists. Start VM, run Compose, check health and smoke tests. Mac stores a Git bundle plus MLflow/DVC backup; see the resume guide. |

## Pages and commands to have open

- Browser: UI `:8501/index.html`, pipeline `:8501/pipeline.html`, FastAPI `:8000/docs`, MLflow tracking `:5000` if started, Prometheus `:9091/targets`, Grafana `:3001`.
- Terminal: `docker compose ps`; `dvc dag`; `dvc status -c`; `python scripts/phase6_tests.py`; `python scripts/phase5_smoke.py`; `python scripts/phase7_verify.py` from the project environment.
- Files: `docs/architecture.md`, `docs/model_card.md`, `reports/model_evaluation.json`, `reports/etl_benchmark.md`, `reports/final_acceptance.md`.
