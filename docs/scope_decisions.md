# Approved submission scope and limits

The original blueprint is a broader implementation plan, not a record of completed work. Following course-material review, the user authorized closing professor-facing gaps with a local DVC/MLproject workflow and honest reduced scope.

- Primary compute and CI run in the Ubuntu VM. GitHub stores the private repository; historical hosted CI runs are preserved but no longer triggered automatically. No interpretation of professor approval for hosted compute is asserted.
- Ray Core demonstrates parallel ETL; no Ray Tune/Train/Serve claim. Spark and Ray satisfy the rubric's alternative data-engineering options. Airflow is taught broadly but not explicitly required by the final rubric; DVC handles this small workflow. Kubernetes/KServe, fleet replay, role accounts and approved-feedback learning remain deferred extensions.
- The DVC DAG includes pinned source validation, independent ETL, comparison, fixed split, validation-only candidate training/evaluation and manifest packaging. Deployment remains an explicit gated operation.
- New runs log clean source SHA, data/split/artifact hashes and parameters. The original selected run's uncommitted-source limitation cannot be retroactively repaired. The frozen test evaluation is not rerun.
- Predictions are model scores on synthetic records. No future-failure, calibrated field probability, real drift/performance-degradation or newly improved model claim is made.
- Local loopback deployment has no user authentication/TLS or encrypted-storage proof. This security scope must remain visible. Live metrics do not cover every offline process internally.
- The declared environment snapshot records installed versions; it is not a cryptographic package/image lock or proof of fresh offline environment installation. Existing Docker images and persistent DVC/MLflow storage are needed for the current restart workflow.
- AI disclosure remains explicitly deferred by the user. A final submission still requires its later review and the user's viva preparation.
