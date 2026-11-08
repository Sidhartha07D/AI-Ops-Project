# Final-project requirements and evidence matrix

The professor's evaluation guideline defines 25 points. The original blueprint is a larger implementation plan; approved scope reductions are in `docs/scope_decisions.md`. This matrix describes implemented coverage, not promised marks. Current observed results and exact counts are in `reports/submission_acceptance.md`; old phase reports are historical.

| Graded area | Implementation and evidence | Limits / final review |
| --- | --- | --- |
| UI/UX (3) | Independent HTML/CSS/JS form, score and inspection result, input limits, feedback flag, responsive captures, Help page and nontechnical manual | No claim of exhaustive browser accessibility testing or a full feedback-label editor |
| Pipeline visualization (2) | Eight DVC stages from pinned validation through candidate training/evaluation/packaging; pipeline screen shows output presence, candidate lineage, last local CI status and expandable actual command outcomes/timings, validation console and tool links | Output presence is not a newly executed job. Whole-pipeline retry/cancel through UI remains outside scope; DVC/CI commands run locally |
| Design (2) | Architecture/block explanation, HLD with lifecycle/release diagram, LLD with endpoints and I/O, exported live OpenAPI, configurable REST UI boundary | Mermaid diagrams are source diagrams rendered by GitHub; PDF exports depend on final requested submission format |
| Implementation (2) | Functional Python, Ruff formatting and selected critical lint checks, INFO logging, controlled API/model/storage errors, exclusive release lock and tests | Educational local app; no blanket claim of exhaustive exception/security testing |
| Testing (1) | Named plan, exact collected unit counts, local command logs, live integration/model parity, short measured load probe, unit and live recovery fixtures | Acceptance groups are not automated case counts. Short unpaced probe plus a separate two-minute paced measurement; neither proves saturation capacity or a production SLA |
| Data engineering (2) | Independent bounded Spark/Ray feature jobs, row equality, pinned raw validation dependency, fixed split, measured ETL report | One-run framework timing, not scale/cluster superiority; Ray Core ETL rather than Ray Tune/Train |
| Source control/CI (2) | Git and DVC data/model hashes; eight-stage lifecycle DAG; `scripts/local_ci.py` runs tests, reproduction, local artifact backup and runtime checks; recorded fresh-checkout/DVC restore drill | Primary CI is VM-only. Historical hosted Actions preserved and manual-only; no assumed cloud exception |
| Experiment tracking (2) | Original model comparisons and artifacts; clean-source validation-only candidate runs with source/data/split/artifact identity, full estimator/config parameters, validation metrics and importance | Original selected run's dirty-source limitation remains disclosed. Frozen test evaluation is guarded against accidental repeats |
| Monitoring (2) | API counters/gauges/histograms, model/UI/Grafana probes, node exporter, Prometheus/blackbox self scrapes, provisioned Grafana, drift/report freshness gauges and five-minute user timer | No real-label model-quality proof; inputs include repeated demos/tests. MLflow and offline jobs are on demand; persistent reports are not internal live process metrics |
| Packaging (2) | MLflow model server, declared parameterized MLproject/environment snapshot, API code baked into image, separate Nginx UI/API/model Compose services | API workspace mount remains for local DVC/data access. Environment versions checked in the existing env; fresh installation/image distribution was not reproduced here |
| Viva (5) | Project/tool/design guide and course review | Personal explanation/defence and Assignments 1–10 rehearsal require the student; not marked passed by software tests |

## Mandatory documents

- Architecture and blocks: `docs/architecture.md`.
- HLD and rationale/diagram: `docs/high_level_design.md`.
- LLD endpoint I/O and actual schema: `docs/low_level_design.md`, `docs/openapi.json`.
- Test plan/cases and observed report: `docs/test_plan.md`, `reports/submission_acceptance.md`.
- Nontechnical manual: `docs/user_manual.md`, browser `ui/manual.html`.

## Remaining submission decisions

- The AI disclosure remains deferred by explicit user instruction; do not submit without the later required review.
- Confirm instructor access to the private repository and the requested archive/PDF/video format.
- Rehearse the actual project and assignment concepts. No full-mark guarantee is made.
- Evidence index corrections matter: mislabelled screenshot 26 was removed. Genuine UI outage/recovery captures 31/32 and the saved-results terminal capture 33 were inspected and saved.
- Airflow/KServe/Kubernetes, fleet replay, role accounts and feedback-to-training workflow are explicit deferred extensions, not silently completed requirements.
