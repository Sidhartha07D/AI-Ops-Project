# Smart Maintenance Monitor

DA3408 course project using the UCI AI4I 2020 Predictive Maintenance dataset.

This project will build an observation-level machine failure classifier and demonstrate a reproducible AIOps workflow: data versioning, distributed data processing, experiment tracking, model serving, a user interface, container orchestration, and monitoring.

The project is developed incrementally in an Ubuntu ARM64 VM. Model metrics will be reported honestly; the main learning goal is to demonstrate the tools and workflow.

The five course documents are `docs/architecture.md`, `docs/high_level_design.md`, `docs/low_level_design.md`, `docs/test_plan.md`, and `docs/user_manual.md`. `docs/requirements_matrix.md` maps them and the observed results to the professor's rubric. The browser API address is set in `ui/config.js`.

## Data preparation

Activate the `smart-maintenance` environment and run `dvc repro` to prepare the raw CSV with Spark and Ray. The two jobs are deliberately limited to two local workers and run sequentially on the VM. Run `python src/compare_features.py` to check that their 10,000-row outputs match. See `data/README.md` for source and license details and `docs/feature_schema.md` for the model input columns.

## Exploration and fixed splits

Run `python src/explore_data.py` to regenerate the data audit and figures. The DVC pipeline now compares the Spark/Ray outputs and creates a seeded 60/20/20 stratified ID manifest with a locked test set. `dvc repro` recreates these inputs before training. The split report is in `reports/split_summary.json` after `dvc pull` or reproduction.


## Model experiments (Phase 4)

With the `smart-maintenance` environment active, run `dvc pull`, `dvc repro`, then `python src/explore_data.py`. Start a tracked project run using:

```bash
export MLFLOW_TRACKING_URI="sqlite:////home/sidhartha/smart-maintenance-monitor/mlflow_store/mlflow.db"
mlflow run . -e train --experiment-name smart-maintenance-baselines --env-manager local
```

The training command compares four candidates using validation average precision. It chooses the alert threshold using validation F2, evaluates the locked test set once, logs the selected pipeline and artifacts, and writes `reports/model_evaluation.json`. `mlflow run . -e validate --env-manager local` is a separate data-check entry point. The reproducible model details and limitations are in `docs/model_card.md`.

To inspect the run in the Ubuntu VM browser, start the local tracking page with `mlflow server --backend-store-uri "$MLFLOW_TRACKING_URI" --host 127.0.0.1 --port 5000` and open `http://127.0.0.1:5000` in Firefox. The MLflow store is excluded from Git; export or back it up separately when moving the project.

For safe VM shutdown and restart steps, see [the resume checklist](docs/resume_after_vm_shutdown.md).


## Local serving and UI (Phase 5)

Run `scripts/start_phase5.sh` after booting the VM. It starts the saved MLflow probability model on port 5001, FastAPI on port 8000, and the separate static UI on port 8501. Open `http://127.0.0.1:8501/index.html` in the Ubuntu browser for the machine check, `http://127.0.0.1:8501/pipeline.html` for the pipeline and validation console, and `http://127.0.0.1:8000/docs` for the API interface. `scripts/phase5_smoke.py` checks the local integration. Stop the services with `scripts/stop_phase5.sh` to free RAM.

The API's six-field request and response, validation errors, and feedback queue are described in `docs/api_io.md`. Feedback is stored for human review and is never added to training automatically. All services bind to the VM's loopback interface; the UI and backend have separate processes and files.

## Container deployment and checks (Phase 6)

The exact selected MLflow model is tracked as `models/serving_model.dvc`. After cloning this repository on the same VM, run `dvc pull` before building; the local DVC remote configured in `.dvc/config.local` must also be present. The image build copies this restored model into the model image. To start the three independent services:

```bash
cd ~/smart-maintenance-monitor
scripts/stop_phase5.sh
docker compose up -d --build
docker compose ps
~/miniconda/envs/smart-maintenance/bin/python scripts/phase5_smoke.py
```

Open the same UI, pipeline, and API URLs listed above. Compose binds all published ports to VM localhost. `docker compose logs --tail=50 model api ui` shows service logs. `docker compose down` stops and removes the seven containers; the images, DVC data, feedback, and MLflow runs persist. Do not start the Phase 5 host processes and Compose on the same ports at once.

Focused API tests run with `python scripts/phase6_tests.py` from the project environment. `.github/workflows/checks.yaml` defines push/PR source, unit, pinned UCI download, full DVC repro, Spark/Ray comparison, and Compose configuration checks. The workflow has not been observed on GitHub until this repository is pushed to a remote. The container test results are recorded in `reports/phase6_test_report.md`.

## Monitoring and controlled release (Phase 7)

`docker compose up -d` also starts Prometheus, a probe exporter, a host exporter, and Grafana. In the Ubuntu browser, open `http://127.0.0.1:9091/targets` for live target health and `http://127.0.0.1:3001/d/smart-maintenance/smart-maintenance-monitor-c2b7-live-services` for the provisioned dashboard. The existing VM ports 9090 and 3000 are used by other work, so this project uses 9091 and 3001. All published ports bind to localhost. Prometheus retains at most two days or 256 MB of data. See `docs/operations.md` for metric meanings, drift limits, and release steps.

Run `python scripts/drift_check.py --mode observations` to assess recent API inputs once at least 50 exist. `--mode demo` reproduces the clearly labeled deliberate torque shift comparison; its result is not evidence of real equipment drift. Neither mode triggers retraining automatically.

Two validation-only candidates and their MLflow/DVC artifacts demonstrate the release gate. `python scripts/release_gate.py review <candidate>` checks the split, schema, locked-test exclusion, validation average precision, recall, and model artifact. An operator must explicitly run `promote`; `rollback` restores the prior release and restarts MLflow serving. The real local promote and rollback were tested, and the original model is currently active. Run `python scripts/phase7_verify.py` while Compose is running for the acceptance check. The results are in `reports/phase7_test_report.md`.

## Final checks and evidence (Phase 8)

The professor's five required documents are linked near the top of this README. `reports/final_acceptance.md` records observed pass, partial, and pending results against `docs/test_plan.md`; `docs/viva_guide.md` prepares the short live explanation. The evidence inventory is `evidence/README.md`, with original VM-browser captures in `evidence/screenshots/` and Mac copies under `outputs/evidence/screenshots/` in the Codex workspace.

The CI workflow restores the pinned UCI CSV by checked hash and runs the DVC stages from a fresh checkout. Those commands passed locally and in [GitHub Actions run 42454769012](https://github.com/Sidhartha07D/AI-Ops-Project/actions/runs/42454769012) in the private project repository. A Mac Git bundle plus MLflow/DVC state backup was restored in a disposable VM directory and passed source, feature, model-artifact, and tracking-database checks. The final AI-use disclosure is intentionally deferred until submission review.
