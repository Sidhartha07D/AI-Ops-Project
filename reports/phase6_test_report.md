# Phase 6 container and API check report

Observed on 2026-11-07, Ubuntu 26.04 ARM64 UTM VM, local Compose deployment. These checks use the selected DVC-tracked model and actual localhost services.

| Check | Acceptance criterion | Observed result |
| --- | --- | --- |
| Build and start | Model, API, and UI images build; three containers healthy | PASS, `docker compose build model api` and `docker compose ps` |
| Model and API | `/health` reports both ready | PASS |
| Routine prediction | Probability in [0,1], no inspection alert | PASS, 0.011700 |
| Inspection prediction | Alert at or above selected threshold | PASS, 0.950276 |
| Bad input | API returns HTTP 422 | PASS |
| Pipeline | Four DVC stages present, remote in sync | PASS |
| Validation job | Real job returns success and console says `Validation: PASS` | PASS |
| Feedback | Request accepted into pending review queue | PASS, HTTP 202 |
| UI | Both independent UI pages return HTML | PASS |
| API unit cases | Feature mapping, threshold boundary, invalid reading, bad model response | PASS, four tests |
| Source and configuration | Python compile, `dvc dag`, Compose syntax | PASS |

Commands: `python scripts/phase6_tests.py`, `python scripts/phase5_smoke.py`, `python -m compileall -q api src scripts`, `dvc dag`, and `docker compose config --quiet`, using the `smart-maintenance` Python environment. The API request and browser UI use the same selected run ID. The two UI demo readings are from the training set and do not constitute new test-set evaluation.

At measurement, all three containers were healthy and the VM had 5.3 GiB of free storage. Model and API images together occupied about 2.7 GB of Docker image storage. The CI workflow is defined, but no GitHub runner result is claimed here. Browser screenshot evidence is indexed separately in `evidence/README.md`.
