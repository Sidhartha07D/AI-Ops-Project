# High-level design and choices

## User workflow

1. A user opens the local UI, enters a machine type and five numeric sensor values, or loads a labeled sample.
2. The browser sends a six-field JSON record to FastAPI. It does not know the model's internal preprocessing schema.
3. FastAPI validates ranges, derives `temperature_gap_k`, and asks MLflow serving for the two class probabilities.
4. FastAPI applies the released alert threshold and returns a probability, recommendation, model run ID, and interpretation. The UI displays an inspection flag or routine check. A person makes the maintenance decision.
5. A separate pipeline page shows the DVC stage state and a real validation-job console. Feedback enters a pending human-review queue; it never retrains automatically.

## Design decisions

| Decision | Reason and trade-off |
| --- | --- |
| Observation-level classifier | AI4I's supplied label is for the same record; there is no time-to-failure horizon. Honest scope is more defensible than claiming a forecast. |
| UCI synthetic source, pinned hash | Small enough for the VM, legally reusable, and reproducible. Synthetic data cannot validate performance on real industrial assets. |
| Spark and Ray, run sequentially | Demonstrates both course data tools without exhausting 3.3 GiB RAM. Their 10,000-row outputs are compared row by row. Startup dominates this small workload. |
| Fixed stratified 60/20/20 split | Validation selects candidate and threshold; the test split was evaluated once. No equipment/time grouping is possible from the dataset fields. |
| Average precision for selection, validation F2 for alert threshold | Failures are rare (339/10,000), so accuracy alone would be misleading. F2 favors recall for an inspection aid. Both false alarms and missed failures remain visible in the confusion matrix. |
| MLflow tracking and serving | MLflow run IDs connect metrics and artifacts to the model endpoint. The saved pipeline contains preprocessing and classifier together. |
| DVC for data and model artifacts, Git for source | Large or generated artifacts stay out of Git while hashes and dependencies remain versioned. The VM-local DVC remote must be backed up separately. |
| Independent static UI, FastAPI, and model server | Clear REST boundaries and separate Compose services. `ui/config.js` selects the API origin; `SMART_MAINTENANCE_MODEL_URL` selects the model endpoint. |
| Human-command release gate | Drift or feedback cannot silently replace a model. A candidate must retain the split/schema, avoid the locked test, and match or exceed champion validation AP and recall. Promotion and rollback restart the model service. |
| Local monitoring | Prometheus scrapes API/host metrics and probes model/UI; Grafana shows them in a 10-second-refresh dashboard. No external notification or cloud deployment is used. |

## Quality and failure behavior

Input ranges are checked both in the browser and FastAPI. FastAPI returns 422 for invalid inputs, 503 when the model cannot be reached, and 502 for malformed or nonfinite model predictions. The UI shows service failures rather than a fabricated score. The validation job records its exit status and console output, whether it succeeds or fails. The API logs requests, model failures, feedback IDs, and job outcomes without logging full sensor values; a separate local observation file supports drift analysis. Prometheus rules detect API availability, model/UI probe failure, and API 5xx errors.

The API and UI are local-only. Grafana permits anonymous viewing because its published port binds to loopback and the dashboard contains only course-demo metrics. This is a constrained educational design, not an authenticated production portal. Release decisions and model provenance are recorded, but the original selected MLflow run began with an uncommitted training script; the model card discloses this and the final code is committed. Phase 8 will add an observed reproducibility and CI record.

## Performance and capacity

One local Spark run prepared 10,000 rows in 7.62 seconds (1,312 rows/s); one Ray run took 4.37 seconds (2,288 rows/s). These include startup and CSV writing and are not scale benchmarks. The model had locked-test average precision 0.8066 and recall 0.8529 at threshold 0.37. The metrics describe a synthetic, randomly split dataset; they do not establish field reliability. Docker images and monitoring storage are bounded to fit the VM. See `reports/etl_benchmark.md`, `docs/model_card.md`, and `docs/operations.md` for the measured details.
