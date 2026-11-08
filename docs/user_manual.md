# Smart Maintenance Monitor: user manual

## What this tool does

This local course demonstration checks one machine reading from the synthetic AI4I 2020 dataset. It estimates whether the **current record** resembles a machine-failure record. It does not forecast when a real machine will fail. An inspection recommendation is a prompt for a human check, not an automatic maintenance order.

## Open the application

After the project operator starts the VM services, open Firefox **inside the Ubuntu VM** and visit `http://127.0.0.1:8501/index.html`. The status at the top should show the model and API as ready. If it does not, ask the operator to start the services; do not treat a stale page as a result.

## Check a reading

1. Enter the machine's product type (`L`, `M`, or `H`), air and process temperatures in Kelvin, rotation speed in rpm, torque in Nm, and tool wear in minutes. The form labels show the accepted ranges.
2. Select **Check reading**. The page shows a model failure score, alert decision, recommendation, model run, and response time.
3. **Continue routine checks** means this record is below the saved alert threshold. **Schedule an inspection** means the record meets or exceeds it. A score is a model output on synthetic data; use ordinary safety procedures and judgment for real equipment.
4. For a guided demonstration, choose **Routine sample** or **Inspection sample**, then **Check reading**. These are examples, not live sensor measurements.

If a field is out of range or missing, correct it and submit again. If the page says the model is unavailable, contact the operator; no prediction has been produced. The application never changes the model because a user submits a reading. During a release change it may ask you to retry shortly.

## Submit feedback

After a prediction, select **Flag this result for review**. The current UI records a flag; it does not offer a note editor or outcome-label form. Feedback is saved for human review. It does not immediately retrain the model or change the alert threshold.

## Inspect the pipeline

Open **Pipeline status** from the application. The stage list shows whether expected files are present; the separate DVC status describes whether the versioned remote is in sync. Select **Run validation** to recheck the pinned source CSV. The console shows the real result and either success or error. Validation does not retrain the model.

## For the project operator

From `~/smart-maintenance-monitor`, start all services with `docker compose up -d`, then verify `docker compose ps` and run `~/miniconda/envs/smart-maintenance/bin/python scripts/phase5_smoke.py`. Open `http://127.0.0.1:8000/docs` for API definitions, `http://127.0.0.1:9091/targets` for checks, and `http://127.0.0.1:3001` for Grafana. Use `docker compose down` before shutting down the VM. If the VM has been off, follow `docs/resume_after_vm_shutdown.md`. For release review and rollback, follow `docs/operations.md`. The app uses only local VM storage and loopback ports.
