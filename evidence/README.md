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
| `13_phase5_ui_inspection_alert.jpg` | Inspection example produces a real alert above the selected threshold | Ubuntu Firefox, same UI, 18:10 VM time |
| `14_phase5_pipeline_console.jpg` | DVC stage state and successful validation job with real console output | Ubuntu Firefox, `http://127.0.0.1:8501/pipeline.html`, 18:11 VM time |
| `15_phase5_fastapi_docs.jpg` | Independent FastAPI endpoint documentation | Ubuntu Firefox, `http://127.0.0.1:8000/docs`, 18:12 VM time |

The failed MLflow runs visible in the first browser screenshot came from initial project-entry-point and model-serialization setup errors. They are retained as an honest execution history. The later successful run is the one recorded in the model card and evaluation report.

The two UI examples are training-set records used only for demonstration; they are not additional locked-test evaluations. The integration smoke script also checks an invalid-input 422 response, a model prediction, DVC status, validation, feedback queue, and the UI service.
