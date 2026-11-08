# Smart Maintenance Monitor: narrated demonstration

Required duration: 5–10 minutes. Target: **7 minutes 30 seconds**. This is a recording plan and suggested talk track, not a completed video. Rehearse once with a stopwatch; allow time for navigation. Speak in your own words and explain every command you show.

## Before recording

- Start the Ubuntu VM and run `docker compose up -d --wait` from `~/smart-maintenance-monitor`.
- Keep the UI, pipeline, API docs, MLflow and Grafana tabs ready inside Ubuntu. Aim for readable 80–100% browser zoom; use 67% only when necessary to fit the result. Maximize the VM.
- Start MLflow tracking on demand using `docs/resume_after_vm_shutdown.md`; open the `smart-maintenance-baselines` experiment and the selected run. Have the newer validation-only candidate run available too.
- Open the PDF architecture page and a terminal showing `reports/verification_summary.txt`. Prepare `dvc dag`, `docker compose ps` and `git status --short --branch`.
- Use your recorder's screen plus your own microphone. Check a 15-second sample for readable text and audible narration before recording the full demonstration. A 1080p recording is sufficient. Do not include passwords, personal notifications or GitHub tokens.
- Show actual local pages. When using a saved screenshot/report, say it is saved evidence. Do not call cached DVC stages fresh training or say the old selected run has clean source history.
- Do not spend two minutes rerunning the sustained probe on camera. Show its real report and describe its pacing and measurement.

## Timed sequence and suggested narration

### 0:00–0:40 | Problem and scope

**Show:** UI header, then report title/architecture briefly.

“My project is Smart Maintenance Monitor for DA3408. It takes a current equipment reading and classifies it using a saved model. The operator gets either routine-check guidance or an inspection flag. The dataset is the synthetic UCI AI4I 2020 dataset, so this is record classification, not a prediction of when a real machine will fail. My main focus is demonstrating the complete local AIOps workflow: preparation, versioning, experiment tracking, deployment, monitoring and recovery. Everything needed for the primary compute workflow runs in this Ubuntu VM.”

### 0:40–1:45 | Operator experience and validation

**Show:** Load Routine sample → Check reading; then Inspection sample → Check reading. Explain the displayed run/threshold. Enter torque 200 and attempt submission; restore the sample afterward. Briefly open Help.

“The frontend is separate from inference. These sample readings are training-set examples used only for demonstration. This first result recommends routine checks. The second triggers an inspection at the selected threshold of 0.37. The displayed percentage is an uncalibrated model score, not a calibrated industrial failure probability. The interface shows the model identity and an explanation. Here an out-of-range torque is blocked by the browser; the server validates inputs independently as well. A user can flag an existing result for review. That flag queues feedback; it does not approve a label or retrain the model. Help explains the workflow for a nontechnical user.”

### 1:45–2:50 | Data pipeline and DVC

**Show:** Pipeline screen; expand the real CI/job outcome list; run validation. Show `dvc dag` in the terminal if the diagram is clearer there. Open the measured ETL report briefly.

“There are eight DVC stages. They validate the pinned source, prepare features independently with Spark and Ray, compare them, create fixed splits, train a candidate, evaluate it on validation data and package a candidate manifest. Both ETL jobs processed 10,000 rows and produced identical outputs. The recorded local timing was 7.62 seconds for Spark and 4.37 seconds for Ray, including startup and CSV output. This small one-run measurement does not establish large-cluster superiority. DVC records dependencies and data/model identities; Git records source and configuration. The screen distinguishes files being present from an actual job execution. This console shows the real validation result. Cached stages are correctly reused rather than described as newly trained.”

### 2:50–3:55 | MLflow and reproducibility

**Show:** Initial experiment comparison; selected metrics and confusion artifact; newer candidate tags/metrics.

“I compared a dummy baseline, logistic regression, histogram gradient boosting and a bounded random forest. The random forest had validation average precision about 0.7495. MLflow stores parameters, metrics and artifacts. The newer candidate records clean source, data, split and model identities and scores only the 2,000 validation records after fitting on 6,000 training records. It uses zero frozen-test rows. Permutation importance is also logged, with the limitation that correlated features affect interpretation. The original selected run has a disclosed source-history limitation, and test metrics appear in a failed packaging run and the successful retry. I preserve that history rather than claiming it was repaired. The new clean candidate is a reproducibility improvement, not a claimed accuracy improvement.”

### 3:55–4:45 | Architecture, APIs and packaging

**Show:** Architecture diagram, `docker compose ps`, then `http://127.0.0.1:8000/docs`.

“The browser calls configurable FastAPI endpoints. FastAPI validates the request, derives the temperature gap, calls the separate MLflow model server and applies the active policy. The frontend, API and model are separate Compose services. Monitoring adds four more services. OpenAPI exposes the request and response contracts. Invalid input returns 422; an unavailable model returns a controlled 503 when inference is requested; malformed model output returns 502. API code is included in its image, while the workspace provides local data and DVC reports. MLproject and the environment snapshot declare the workflow and check the installed versions. I have not claimed a fresh offline environment installation.”

### 4:45–5:50 | Monitoring and drift

**Show:** Grafana availability, request/latency, host memory/disk, drift count and report age. Briefly show Prometheus targets.

“Prometheus collects application counters, latency and readiness. Blackbox probes check model, UI and Grafana endpoints, and node exporter supplies VM resources. Grafana combines them. The drift timer runs every five minutes while the user manager is active. It needs at least 50 observations and reads up to 500 recent successful inputs. The dashboard shows both sample count and report age so an old report is visible. These recent records include repeated tests and demonstrations. Input drift is not the same as newly labeled model-performance degradation. MLflow and offline jobs are on demand; I do not claim every offline process has continuous internal metrics.”

### 5:50–6:45 | Tests, performance and restore

**Show:** `cat reports/verification_summary.txt`; then the stored sustained-load and restore reports if needed. Use screenshot 31 briefly for the recorded outage, followed by the recovered UI.

“The latest recorded local verification passed all 13 collected unit cases and all 13 CI command groups. Those are separate counts. CI checks formatting, environment, tests, DVC reproduction and local backup, feature parity, configuration, live integration, model/API agreement, drift and operations. A separate two-minute paced test completed 240 requests with zero errors and p95 about 102 milliseconds. That measures two paced clients, not saturation capacity or a production SLA. A fresh checkout restored both model artifacts from DVC and loaded the model successfully. This saved outage capture shows the genuine unavailable-model warning; after restoration the live integration and inspection result worked again. A full Ubuntu reboot was also verified: its boot ID changed, saved models and policy were preserved, and the project restarted successfully.”

### 6:45–7:30 | Release safeguards and closing scope

**Show:** Release/recovery report and required-document list; finish on the healthy UI.

“An eligible candidate is not automatically deployed. The release gate checks actual model bytes and recomputes validation metrics before a human-triggered promotion. A shared/exclusive lock protects requests during a switch. Real promotion, rollback and injected-failure recovery were tested. Switching has downtime, and recovery failure requires operator attention. DVC handles this small lifecycle, so Airflow and Kubernetes were not added as unnecessary platforms. Source, design documents, manual, exact reports and genuine evidence are included for review. The project demonstrates the implemented local workflow; role accounts, fleet replay, feedback-approved retraining and production security remain documented extensions.”

## Final recording check

- Check the actual file duration: at least 5:00 and no more than 10:00. Target 7:00–8:00 after rehearsal.
- Make sure text and narration are understandable, all local pages shown are real, and services are healthy at the end.
- Keep live demonstration separate from saved-result inspection in the narration.
- The full VM reboot passed and is recorded in `reports/vm_reboot_check.json`; distinguish it from the earlier Compose-only service restart.
- If the video exceeds ten minutes, shorten navigation and discussion of historical metrics; preserve the UI, DVC, MLflow, Compose/API, monitoring and test evidence.
