# DA3408 requirements and evidence matrix

Source of requirements: `AI Application Evaluation Guideline.pdf` (25 points) and `AI Application Development Guidelines.pdf` in the DA3408 course repository. The separate Smart Maintenance Monitor blueprint is our implementation plan; a planned feature is not evidence that it works. Update each row only after observing a real result.

## Eight incremental phases

| Phase | Exit result | Current status |
| --- | --- | --- |
| 1. Foundation | Clean Git project, isolated Python environment, VM budget | Verified; screenshot still to collect |
| 2. Data and DVC | Source/license, validation, raw data pointer and restore | Verified; validation/DVC screenshot saved |
| 3. Spark and Ray | Bounded jobs, matching outputs, DVC DAG | Verified; two screenshots saved |
| 4. Models and MLflow | EDA, leak-safe split, baseline/candidates, metrics, MLflow runs and MLproject | Verified; MLflow browser evidence saved |
| 5. Serving and UI | MLflow model endpoint, FastAPI, independent nontechnical UI, pipeline screen, feedback | Verified with integration test and VM-browser screenshots |
| 6. Packaging and tests | Separate Docker Compose services, logs, unit/integration/end-to-end tests | Three healthy services, tests, and VM-browser evidence verified; GitHub CI run pending |
| 7. Operations | Prometheus/Grafana, drift, retraining gate, release/reject/rollback; isolated KServe exercise if feasible | Live API/model/UI monitoring, drift guard, validation-only candidates, reject/promote/rollback verified; KServe not run on this VM |
| 8. Submission | Five mandatory documents, test report, backups/restore, evidence audit, demo and viva | Pending |

## Evaluation criteria (25 points)

| Rubric area | Required observed result | Status / evidence |
| --- | --- | --- |
| Demo: UI/UX (3) | Intuitive, responsive, foolproof nontechnical UI; no UI errors; user manual | Separate responsive UI and input checks verified; final user manual pending phase 8 |
| Demo: pipeline view (2) | Separate pipeline view or coordinated MLOps UIs; job/error/success console; measured speed and throughput | Live pipeline and successful job console in `evidence/screenshots/14_phase5_pipeline_console.jpg`; DVC DAG and ETL timing also saved |
| Software design (2) | Architecture diagram, HLD, LLD with REST I/O, independent UI and inference blocks | Pending, phases 5/8 |
| Implementation (2) | Consistent Python style, logging, exception handling, inline documentation, API matching LLD, unit tests | Four API unit tests pass; complete LLD and review in phase 8 |
| Testing (1) | Test plan, cases, acceptance criteria, pass/fail report and acceptance result | Phase 6/7 observed reports exist; final unified plan and acceptance report pending phase 8 |
| Data engineering (2) | Automated Spark or Ray or Kubernetes pipeline; measured speed and throughput | Spark and Ray jobs verified in `evidence/screenshots/06_phase3_spark_ray_comparison.jpg`; speed/throughput in `reports/etl_benchmark.md` |
| Source control and CI (2) | Git plus DVC DAG, automated DVC CI, versioned data/model artifacts, restore proof | Git/DVC/DAG/restore and model artifact verified; CI workflow defined but GitHub run pending |
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

- [ ] Architecture diagram with explanation of each block.
- [ ] High-level design with design choices and rationale.
- [ ] Low-level design with endpoint definitions and input/output contracts.
- [ ] Test plan and test cases, followed by an observed test report.
- [ ] Nontechnical user manual.

## Evidence plan

Target 30-40 **distinct, useful** screenshots across the eight phases, with a short recording only for flows that are hard to prove in one image. Prioritize UCI provenance, data validation, DVC DAG/restore, Spark/Ray output and throughput, MLflow runs/artifacts/MLproject, MLflow serving, FastAPI docs and error responses, the live UI and pipeline console, Compose services, Prometheus targets, Grafana panels, drift and rollback, test report, and final offline demo. Capture localhost pages in the VM browser after those services exist. Record the observed URL, time, command or action, and result for each screenshot. Never use mock or copied screenshots as execution evidence.

Currently saved: three Phase 3 screenshots in `evidence/screenshots/`. A Phase 2 validation/DVC screenshot is also saved. The earlier `00_utm_capture_test.jpg` is only a capture test in the chat's local workspace and does not count toward the project evidence target.
