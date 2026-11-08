# DA3408 requirements and evidence matrix

Source of requirements: `AI Application Evaluation Guideline.pdf` (25 points) and `AI Application Development Guidelines.pdf` in the DA3408 course repository. The separate Smart Maintenance Monitor blueprint is our implementation plan; a planned feature is not evidence that it works. Update each row only after observing a real result.

## Eight incremental phases

| Phase | Exit result | Current status |
| --- | --- | --- |
| 1. Foundation | Clean Git project, isolated Python environment, VM budget | Verified; environment and Git state documented |
| 2. Data and DVC | Source/license, validation, raw data pointer and restore | Verified; validation/DVC screenshot saved |
| 3. Spark and Ray | Bounded jobs, matching outputs, DVC DAG | Verified; two screenshots saved |
| 4. Models and MLflow | EDA, leak-safe split, baseline/candidates, metrics, MLflow runs and MLproject | Verified; MLflow browser evidence saved |
| 5. Serving and UI | MLflow model endpoint, FastAPI, independent nontechnical UI, pipeline screen, feedback | Verified with integration test and VM-browser screenshots |
| 6. Packaging and tests | Separate Docker Compose services, logs, unit/integration/end-to-end tests | Seven services healthy; seven API tests and integration smoke pass; hosted CI passed |
| 7. Operations | Prometheus/Grafana, drift, retraining gate, release/reject/rollback | Live API/model/UI monitoring, drift guard, validation-only candidates, reject/promote/rollback verified |
| 8. Submission | Five mandatory documents, test report, backups/restore, evidence audit, demo and viva | Five documents written; Mac backup restoration and hosted CI passed; final evidence and viva work in progress |

## Evaluation criteria (25 points)

| Rubric area | Required observed result | Status / evidence |
| --- | --- | --- |
| Demo: UI/UX (3) | Intuitive, responsive, foolproof nontechnical UI; no UI errors; user manual | Separate UI and input checks verified; 390-pixel view and range warning captured in screenshots 23–24; user manual written |
| Demo: pipeline view (2) | Separate pipeline view or coordinated MLOps UIs; job/error/success console; measured speed and throughput | Success console in `evidence/screenshots/14_phase5_pipeline_console.jpg`, real failure in screenshot 22; DVC DAG and ETL timing saved |
| Software design (2) | Architecture diagram, HLD, LLD with REST I/O, independent UI and inference blocks | `docs/architecture.md`, `docs/high_level_design.md`, `docs/low_level_design.md` written against running system |
| Implementation (2) | Consistent Python style, logging, exception handling, inline documentation, API matching LLD, unit tests | Seven API unit tests pass; logging and model error handling checked; configurable UI API origin |
| Testing (1) | Test plan, cases, acceptance criteria, pass/fail report and acceptance result | `docs/test_plan.md` and observed `reports/final_acceptance.md` complete, with failures and pending personal viva work distinguished |
| Data engineering (2) | Automated Spark or Ray or Kubernetes pipeline; measured speed and throughput | Spark and Ray jobs verified in `evidence/screenshots/06_phase3_spark_ray_comparison.jpg`; speed/throughput in `reports/etl_benchmark.md` |
| Source control and CI (2) | Git plus DVC DAG, automated DVC CI, versioned data/model artifacts, restore proof | Git/DVC/DAG and model artifact verified; full CI passed in a fresh clone and on GitHub Actions run `42454769012`; Mac backup restore passed |
| Experiment tracking (2) | MLflow runs with parameters, metrics, artifacts and custom metadata beyond autologging | Four candidate runs, selected-model run, provenance tags, metrics, artifacts and MLproject verified |
| Monitoring (2) | Prometheus instrumentation of components, Grafana near-real-time views | API and VM metrics, model/UI probes, four targets up, Grafana dashboard and alert rules verified; screenshots 18-19 |
| Packaging (2) | MLflow model serving, MLproject, FastAPI, independent frontend/backend containers in Compose | Model, API, and UI Compose services healthy; integration smoke passed |
| Viva (5) | Explain system, assignments 1-10, tools/use cases, design decisions and challenges | Pending, phase 8 |

## Development-guideline coverage

| Requirement | Planned proof |
| --- | --- |
| Automation, reproducibility, version control and CI | DVC DAG and scripted CI, Git SHA plus MLflow run ID, restore/re-run record |
| Data source, EDA, quality and leakage control | UCI data card, EDA and split reports, validation script, excluded ID/failure-mode fields |
| Model training, comparison and explainability | Baseline and candidates, explicit metrics/thresholds, MLflow artifacts, model card |
| Deployment, parity and rollback | MLproject, Docker Compose, versioned release and observed rollback |
| Monitoring, drift and retraining | API/model/system metrics, Grafana, controlled drift demonstration, reviewed feedback and retrain gate |
| Testing, security and documentation | Unit/integration/end-to-end tests, error cases, test report, role/access notes, five documents |
| Local-only rule | No cloud platform or paid inference API |

## Mandatory documents

- [x] Architecture diagram with explanation of each block.
- [x] High-level design with design choices and rationale.
- [x] Low-level design with endpoint definitions and input/output contracts.
- [x] Test plan and test cases with an observed acceptance report.
- [x] Nontechnical user manual.

## Evidence plan

Target 30-40 **distinct, useful** screenshots across the eight phases, with a short recording only for flows that are hard to prove in one image. Prioritize UCI provenance, data validation, DVC DAG/restore, Spark/Ray output and throughput, MLflow runs/artifacts/MLproject, MLflow serving, FastAPI docs and error responses, the live UI and pipeline console, Compose services, Prometheus targets, Grafana panels, drift and rollback, test report, and final offline demo. Capture localhost pages in the VM browser after those services exist. Record the observed URL, time, command or action, and result for each screenshot. Never use mock or copied screenshots as execution evidence.

The indexed captures in `evidence/README.md` are the evidence inventory. The 24 real captures through screenshot 28 cover the major working screens, error paths, hosted CI and final VM state. The earlier capture tests in the Mac workspace do not count toward the project evidence target.
