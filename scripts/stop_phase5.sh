#!/usr/bin/env bash
set -euo pipefail
root="$HOME/smart-maintenance-monitor/mlflow_store"
for service in ui api model; do
  file="$root/$service.pid"
  if [[ -f "$file" ]]; then
    pid="$(cat "$file")"
    if [[ "$pid" =~ ^[0-9]+$ ]]; then kill "$pid" 2>/dev/null || true; fi
    rm -f "$file"
  fi
done
echo "Stopped Phase 5 services started by start_phase5.sh"
