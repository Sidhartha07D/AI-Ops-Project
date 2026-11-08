# Smart Maintenance Monitor — DA3408

Local CPU application demonstrating an AIOps lifecycle on the UCI AI4I 2020 synthetic dataset. It classifies a current observation; it does not forecast a machine's future failure time. Model scores are not claimed to be calibrated industrial probabilities.

## Start and verify in the Ubuntu VM

```bash
cd ~/smart-maintenance-monitor
export PATH="$HOME/miniconda/envs/smart-maintenance/bin:$PATH"
docker compose up -d
docker compose ps
python scripts/local_ci.py
```

Wait for API/model/UI health before checks. Primary CI runs in the VM. GitHub stores source; historical hosted Actions passes are retained, but automatic hosted triggers are disabled. Offline work uses the existing `smart-maintenance` environment. `MLproject` declares `environment.snapshot.yml` and verifies installed versions; a fresh environment installation is not claimed by that version check.

| View | URL inside Ubuntu Firefox |
| --- | --- |
| Machine check and Help | http://127.0.0.1:8501/index.html |
| Lifecycle and validation console | http://127.0.0.1:8501/pipeline.html |
| FastAPI | http://127.0.0.1:8000/docs |
| Prometheus targets | http://127.0.0.1:9091/targets |
| Grafana | http://127.0.0.1:3001 |
| MLflow tracking, when started | http://127.0.0.1:5000 |

The model is served separately on port 5001. All published ports bind to VM loopback. The UI API URL is in `ui/config.js`. Stop the stack with `docker compose down` before shutting down the VM. See [restart and recovery](docs/resume_after_vm_shutdown.md).

## Current local workflow

`dvc repro` runs or reuses eight dependency-tracked stages: pinned source validation, Spark preparation, Ray preparation, output comparison, fixed split, candidate training, validation evaluation/importance, and candidate-manifest packaging. New candidates use 6,000 training and 2,000 validation rows; the frozen 2,000 test rows are not scored by this pipeline. Unchanged stages may be restored from cache and do not create new MLflow experiments.

```bash
python scripts/local_ci.py
mlflow run . -e validate --env-manager local
# Explicit candidate work, normally driven by DVC:
mlflow run . -e train -P config=params.yaml -P name=random_forest_balanced --env-manager local
mlflow run . -e evaluate --env-manager local
```

Commit source/configuration changes before tracked training. DVC/MLflow commands create a candidate, not a deployment. The historical `src/train_models.py` refuses to rerun when the frozen evaluation report exists. Do not remove that guard for demonstration purposes.

## Release and monitoring

`python scripts/release_gate.py review pipeline` checks actual artifact identity, loadability, split integrity and recomputed validation scores. `promote pipeline` is an explicit operator action; `rollback` restores the previous release. The switch blocks predictions, backs up model bytes/policy, recreates serving, checks outputs against the local bundle, and recovers on failure. It has intentional downtime. The original selected model is currently active.

Prometheus scrapes the API, node exporter, itself and blackbox exporter, and probes model/UI/Grafana health. Grafana shows services, request/latency and VM metrics plus drift sample count/report age. The installed user timer refreshes drift every five minutes while the user manager runs; it never deploys models. See [operations](docs/operations.md).

## Results, provenance and evidence

The reported selected model has validation AP 0.7495; reported test AP 0.8066 and recall 0.8529 at threshold 0.37. The original tracking database contains test metrics from a failed packaging run and the successful selected-model run, both with the same AP. We therefore do not claim a single globally untouched test evaluation. The original selected run also began with uncommitted source. These history limitations are documented in [the model card](docs/model_card.md); clean-source validation-only candidate runs are separate evidence.

- [Current actual acceptance results](reports/submission_acceptance.md): counts, command logs, parity/load probe and recovery.
- [Requirements and limits](docs/requirements_matrix.md), [approved reduced scope](docs/scope_decisions.md), [corrections](docs/hardening_changes.md).
- [Evidence index](evidence/README.md): genuine VM captures; file 26 is a mislabelled CI capture and excluded from outage proof.
- [Dataset source and attribution](data/README.md), [ETL benchmark](reports/etl_benchmark.md), [model evaluation](reports/model_evaluation.json).

## Required documents

1. [Architecture and blocks](docs/architecture.md).
2. [High-level design and diagram](docs/high_level_design.md).
3. [Low-level REST design](docs/low_level_design.md) and [actual OpenAPI](docs/openapi.json).
4. [Test plan and cases](docs/test_plan.md), with the observed acceptance report linked above.
5. [Nontechnical manual](docs/user_manual.md), also available through Help in the application.

[Viva notes](docs/viva_guide.md) support rehearsal but do not establish the student's personal readiness.

## Restore and packaging

Git contains source and DVC pointers; actual model/data objects are in the VM-local DVC remote configured outside Git. A fresh clone requires the supplied DVC/state backup or its configured remote and `dvc pull`. MLflow DB/artifacts are backed up separately with the DVC remote on the Mac. A Git clone alone is not the whole runtime bundle.

The API image contains its code under `/opt/smart-maintenance`; mounted `/workspace` supplies DVC/data/runtime reports. Rebuild after API source changes: `docker compose build api && docker compose up -d api`. Model and UI remain separate services. No Kubernetes, KServe, Airflow, Ray Tune/Train/Serve, full feedback-learning workflow, production authentication/TLS, or fresh offline-image installation is claimed. Those boundaries and final submission review items are explicit in the scope document.
