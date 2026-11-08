# Resume Smart Maintenance Monitor after shutting down UTM

## Before closing the VM

Use Ubuntu's **Power Off / Shut Down** menu and wait for it to finish before closing UTM. The project is stored on the VM disk at `/home/sidhartha/smart-maintenance-monitor`.

The project has continued through Phase 8 local acceptance. The DVC data and local remote, including the selected model artifact, are in sync. The MLflow database and run artifacts are in `mlflow_store/`. Mac backups in `outputs/backups/` and screenshot copies in `outputs/evidence/screenshots/` protect the checkpoint separately from the VM disk. The Phase 8 Git/state backup was restored successfully in a disposable VM directory.

## When you reopen UTM

Start the Ubuntu VM, open Terminal, and run:

```bash
cd ~/smart-maintenance-monitor
git status --short --branch
git log -1 --oneline
~/miniconda/envs/smart-maintenance/bin/dvc status -c
test -f mlflow_store/mlflow.db && echo "MLflow database present"
df -h /
hostname -I
```

Expected: Git branch `main` with no changed files, DVC cache and `vmstore` in sync, the MLflow message, and several GB of free disk space. The VM's IP address may change, so share the new `hostname -I` output if SSH does not reconnect.

The MLflow web page at `http://127.0.0.1:5000` is **off by design** to save RAM. Its stored runs persist. When needed, start it from the project directory with:

```bash
~/miniconda/envs/smart-maintenance/bin/mlflow server \
  --backend-store-uri "sqlite:////home/sidhartha/smart-maintenance-monitor/mlflow_store/mlflow.db" \
  --default-artifact-root "file:///home/sidhartha/smart-maintenance-monitor/mlflow_store/artifacts" \
  --host 127.0.0.1 --port 5000
```

Leave that terminal open while viewing MLflow in the VM browser, then press Ctrl+C to free memory. You do **not** need to rerun data preparation or model training merely because the VM was shut down.

## Restart the project demo

Use one of these service modes at a time:

```bash
cd ~/smart-maintenance-monitor
docker compose up -d
docker compose ps
```

The model, API, and UI containers serve `http://127.0.0.1:5001/ping`, `http://127.0.0.1:8000/docs`, and `http://127.0.0.1:8501/index.html`. The Phase 7 stack also provides Prometheus targets at `http://127.0.0.1:9091/targets` and Grafana at `http://127.0.0.1:3001`. Use `docker compose logs --tail=50` to inspect services. Stop with `docker compose down` before closing the VM. Container images remain on disk, so a normal restart does not rebuild them. If rebuilding from a clone, run `dvc pull` first so `models/serving_model/`, `models/active/`, and the candidate model directories exist.

The lighter host-process alternative remains `scripts/start_phase5.sh` and `scripts/stop_phase5.sh`. Feedback, inference observations, and job logs stay on the VM disk and are excluded from Git. The original selected model is active after the tested rollback. The five course documents and current acceptance report are in `docs/` and `reports/submission_acceptance.md`. VM-only CI is the primary path; historical hosted runs are supplementary; the final AI-use disclosure remains for submission review. The local project remains usable after shutdown.

After services become healthy, run `~/miniconda/envs/smart-maintenance/bin/python scripts/local_ci.py` for the full local check. Inspect `systemctl --user status smm-drift.timer` for scheduled drift refresh. The primary submission path uses no hosted compute.

## Latest restart evidence

`reports/service_restart_check.json` records a completed `docker compose down` followed by `docker compose up -d --wait`, healthy endpoints, the active drift timer, and synchronized DVC storage. This recreated the service containers without rebuilding images or retraining. It was not an operating-system reboot; a full shutdown/start demonstration is recorded separately only when actually performed.
