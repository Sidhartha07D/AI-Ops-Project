#!/usr/bin/env bash
set -euo pipefail
root="$HOME/smart-maintenance-monitor"
env_bin="$HOME/miniconda/envs/smart-maintenance/bin"
cd "$root"
mkdir -p mlflow_store
export MLFLOW_TRACKING_URI="sqlite:////home/sidhartha/smart-maintenance-monitor/mlflow_store/mlflow.db"
export PATH="$env_bin:$PATH"

if ! curl -fsS --max-time 2 http://127.0.0.1:5001/ping >/dev/null 2>&1; then
  nohup mlflow models serve -m runs:/e5260d1c99b046f79795c53a4c392575/serving_model --env-manager local --host 127.0.0.1 --port 5001 --workers 1 > mlflow_store/serving.log 2>&1 < /dev/null &
  echo $! > mlflow_store/model.pid
fi
if ! curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  nohup python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 1 > mlflow_store/api.log 2>&1 < /dev/null &
  echo $! > mlflow_store/api.pid
fi
if ! curl -fsS --max-time 2 http://127.0.0.1:8501/index.html >/dev/null 2>&1; then
  nohup python -m http.server 8501 --bind 127.0.0.1 --directory ui > mlflow_store/ui.log 2>&1 < /dev/null &
  echo $! > mlflow_store/ui.pid
fi
for check in "5001/ping" "8000/health" "8501/index.html"; do
  ready=0
  for attempt in {1..30}; do
    if curl -fsS --max-time 2 "http://127.0.0.1:$check" >/dev/null 2>&1; then ready=1; break; fi
    sleep 1
  done
  if [[ "$ready" != 1 ]]; then echo "Service failed: $check" >&2; exit 1; fi
done
echo "Model http://127.0.0.1:5001/ping"
echo "API   http://127.0.0.1:8000/docs"
echo "UI    http://127.0.0.1:8501/index.html"
echo "Phase 5 services: READY"
