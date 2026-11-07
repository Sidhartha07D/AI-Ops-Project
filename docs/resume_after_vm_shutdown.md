# Resume Smart Maintenance Monitor after shutting down UTM

## Before closing the VM

Use Ubuntu's **Power Off / Shut Down** menu and wait for it to finish before closing UTM. The project is stored on the VM disk at `/home/sidhartha/smart-maintenance-monitor`.

The saved Phase 4 checkpoint is Git commit `9d8e870`. The DVC data and local remote are in sync. The MLflow database and model artifacts are in `mlflow_store/`; a separate Mac backup is in `outputs/backups/smart-maintenance-mlflow-phase4.tar.gz` in the Codex workspace. Screenshots are saved in the VM project and the Mac workspace.

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

Expected: Git branch `main` with no changed files, commit `9d8e870` or a newer commit, DVC cache and `vmstore` in sync, the MLflow message, and several GB of free disk space. The VM's IP address may change, so share the new `hostname -I` output if SSH does not reconnect.

The MLflow web page at `http://127.0.0.1:5000` is **off by design** to save RAM. Its stored runs persist. When needed, start it from the project directory with:

```bash
~/miniconda/envs/smart-maintenance/bin/mlflow server \
  --backend-store-uri "sqlite:////home/sidhartha/smart-maintenance-monitor/mlflow_store/mlflow.db" \
  --default-artifact-root "file:///home/sidhartha/smart-maintenance-monitor/mlflow_store/artifacts" \
  --host 127.0.0.1 --port 5000
```

Leave that terminal open while viewing MLflow in the VM browser, then press Ctrl+C to free memory. You do **not** need to rerun data preparation or model training merely because the VM was shut down.

## Next work

Continue with Phase 5: serve the saved probability model, build the FastAPI backend and a separate simple user interface, inspect their localhost pages in the VM browser, and capture the important screenshots. Keep services small and start them one at a time on this 3.3 GiB RAM VM.
