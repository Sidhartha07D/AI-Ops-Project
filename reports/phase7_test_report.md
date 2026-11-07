# Phase 7 observed checks

Executed in the Ubuntu 26.04 ARM64 UTM VM on 2026-11-07 VM time. All named browser pages were opened in Ubuntu Firefox and captured separately.

| Check | Acceptance result |
| --- | --- |
| Seven-service Compose stack | PASS: model, API, UI, blackbox, node exporter, Prometheus, Grafana running; model/API/UI healthy |
| API instrumentation | PASS: request status, prediction, latency, validation, and model-readiness metrics exported |
| Prometheus targets | PASS: API and host scrapes plus both model/UI probes up; `probe_success=1` for both probes |
| Grafana | PASS: provisioned dashboard displayed three Up panels, predictions, request/latency graphs, and host memory/disk panels |
| Alert rules | PASS: Prometheus `promtool` validated config and three rules |
| Integration after release | PASS: predictions, 422, pipeline/DVC, validation job, feedback, UI |
| Deliberate drift check | PASS: control maximum PSI 0.0062, shifted torque PSI 4.6949 versus 0.2 threshold |
| Actual recent-input guard | PASS: eight API inputs yielded `insufficient_samples`; no real drift inference |
| Validation-only retraining | PASS: two MLflow runs and DVC model artifacts; zero locked-test rows used |
| Release gate | PASS: weaker booster rejected; matching random forest approved and served; original model restored and served after rollback |
| DVC sync | PASS: cache and `vmstore` remote in sync after rollback |

At the end of the first dashboard check, the VM had 3.8 GiB free. The first six containers used about 570 MB of RAM at idle, before node exporter was added; this is an observed snapshot, not peak use. The original MLflow model and its matching DVC `active` artifact are the current release. A Kubernetes/KServe runtime was not started on this 3.3 GiB RAM, 39 GiB disk VM; it is not claimed as verified.
