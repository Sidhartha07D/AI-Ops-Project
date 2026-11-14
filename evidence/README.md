# Evidence index

Screenshots are original captures of the Ubuntu VM display. The Mac workspace also keeps a copy of each JPEG under `outputs/evidence/screenshots/`.

| File | Observed result | Capture context |
| --- | --- | --- |
| `04_phase2_data_validation_dvc.jpg` | Source CSV validation and DVC pointer | Ubuntu terminal, Phase 2 |
| `06_phase3_spark_ray_comparison.jpg` | Spark and Ray output checks match | Ubuntu terminal, Phase 3 |
| `07_phase3_dvc_pipeline.jpg` | DVC DAG and remote sync | Ubuntu terminal, Phase 3 |
| `08_phase3_measured_throughput.jpg` | Observed ETL run time and throughput | Ubuntu terminal, Phase 3 |
| `09_phase4_mlflow_runs.jpg` | MLflow experiment with candidate runs and the selected model | Ubuntu Firefox, `http://127.0.0.1:5000`, 2026-11-07 17:30 VM time |
| `10_phase4_mlflow_selected_metrics.jpg` | Selected run metrics, parameters, and provenance tags | Ubuntu Firefox, MLflow run `e5260d1c99b046f79795c53a4c392575`, 17:31 VM time |
| `11_phase4_mlflow_confusion_artifact.jpg` | Logged confusion-matrix artifact preview | Ubuntu Firefox, same run, 17:32 VM time |
| `12_phase5_ui_prediction.jpg` | Separate UI shows six fields and a routine result from the served model | Ubuntu Firefox, `http://127.0.0.1:8501/index.html`, 2026-11-07 18:08 VM time |
| `15_phase5_fastapi_docs.jpg` | Independent FastAPI endpoint documentation | Ubuntu Firefox, `http://127.0.0.1:8000/docs`, 18:12 VM time |
| `16_phase6_compose_ui.jpg` | Containerized UI shows the selected model's 95.0% inspection result, with all services ready | Ubuntu Firefox, `http://127.0.0.1:8501/index.html`, 2026-11-07 18:34 VM time |
| `17_phase6_compose_tests.jpg` | Three healthy Compose services, four passing API unit tests, and VM storage | Ubuntu terminal, `docker compose ps`, `python scripts/phase6_tests.py`, `df -h /`, 18:36 VM time |
| `19_phase7_prometheus_targets.jpg` | API metrics scrape and model/UI probes are all Up | Ubuntu Firefox, `http://127.0.0.1:9091/targets`, 18:56 VM time |
| `20_phase7_drift_release_checks.jpg` | Acceptance check confirms deliberate drift detection, sparse-input guard, release rejection, promotion, rollback, and DVC sync | Ubuntu terminal, `python scripts/phase7_verify.py`, 18:59 VM time |
| `22_phase8_pipeline_error.jpg` | Pipeline page shows a real failed validation job and console traceback from a separate invalid fixture; pinned source was untouched | Ubuntu Firefox, `http://127.0.0.1:8501/pipeline.html`, 2026-11-08 11:36 VM time |
| `23_phase8_responsive_mobile.jpg` | Machine-check page at a 390 × 844 responsive viewport, with header, service status, guidance and input form fitting the narrow width | Ubuntu Firefox Responsive Design Mode, `http://127.0.0.1:8501/index.html`, 2026-11-08 11:43 VM time |
| `24_phase8_ui_input_guard.jpg` | Torque value 200 exceeds the allowed maximum 100; Firefox blocks submission with a visible range message in the narrow viewport | Ubuntu Firefox, same UI, 2026-11-08 11:47 VM time |
| `25_phase8_clean_commit_mlflow.jpg` | Validation-only MLflow run is Finished and identifies clean source commit `91f9214`; no model metrics are claimed for this data-check run | Ubuntu Firefox, MLflow run `71c564ba12294121ab1e4f78e8eeab9e`, 2026-11-08 11:53 VM time |
| `27_phase8_hosted_ci_pass.jpg` | Private GitHub Actions job passes unit, pinned download, DVC repro, Spark/Ray comparison, and Compose checks | Ubuntu terminal, `gh run view` for run `42454769012`, 2026-11-08 12:02 VM time |
| `28_phase8_final_vm_status.jpg` | Clean main branch, seven live services, DVC remote in sync, and 5.2 GiB free on the VM root disk after recovery | Ubuntu terminal, `git status`, `docker compose ps`, `dvc status -c`, `df -h /`, 2026-11-08 12:07 VM time |

The failed MLflow runs visible in the first browser screenshot came from initial project-entry-point and model-serialization setup errors. They are retained as an honest execution history. The later successful run is the one recorded in the model card and evaluation report.

The two UI examples are training-set records used only for demonstration; they are not additional locked-test evaluations. The integration smoke script also checks an invalid-input 422 response, a model prediction, DVC status, validation, feedback queue, and the UI service.

Submission-hardening corrections supersede earlier descriptions. Screenshot 26 was removed because it showed CI terminal output rather than the claimed outage UI. Replacement browser outage/recovery evidence is now recorded in captures 31 and 32.

| New capture | Observed result | Context |
| --- | --- | --- |
| `29_local_lifecycle_pipeline.jpg` | Updated lifecycle page shows candidate validation score, zero test rows scored, local CI passed, DVC sync, and train/evaluate stages with actual validation console | Ubuntu Firefox, 2026-11-08 16:34 IST; exact inspected frame saved |
| `30_scheduled_drift_monitoring.jpg` | API, model and UI Up; latest drift report contains 394 inputs, neutral count colour, report age approximately three minutes; VM memory and disk panels visible | Ubuntu Firefox Grafana, VM clock 2026-11-08 17:10; exact inspected frame saved. Inputs include repeated demo/test requests, not new industrial measurements. |

