# Model card: Smart Maintenance Monitor baseline

## Intended use

This model estimates whether an AI4I 2020 equipment record has the dataset's `Machine failure` label. It is a course demonstration of data preparation, model tracking, and serving. It does **not** predict a future failure horizon or replace a maintenance decision.

## Data and leakage controls

- Source: UCI AI4I 2020 synthetic predictive maintenance data; 10,000 rows and 339 positive labels.
- Inputs: equipment type, air and process temperature, rotational speed, torque, tool wear, and the temperature gap derived from the two temperatures.
- Excluded: UDI, product ID, and all failure-mode flags. The five mode flags would reveal the target at the same record and must never enter training.
- The 27 rows whose supplied main label differs from the OR of the failure-mode flags retain the supplied main label. The discrepancy is recorded in `reports/data_audit.json`.
- Exact duplicate input rows were checked and absent. A fixed, stratified 60/20/20 ID manifest is tracked by DVC; preprocessing is fitted on training data only.

## Selection and results

The candidates were a prior-probability dummy baseline, class-weighted logistic regression, bounded class-weighted random forest, and histogram gradient boosting. The random forest had the best validation average precision (0.7495). A probability threshold of 0.37 maximized validation F2 on a fixed grid. Test metrics were logged during a failed packaging run and the successful selected-model run; both report the same AP. A strict single-evaluation claim is therefore unsupported.

| Locked test metric | Value |
| --- | ---: |
| Average precision | 0.8066 |
| ROC AUC | 0.9692 |
| Recall | 0.8529 |
| Precision | 0.5000 |
| F1 | 0.6304 |
| Brier score | 0.0188 |
| True negatives / false positives | 1,874 / 58 |
| False negatives / true positives | 10 / 58 |

These are one-split demonstration results, not a claim about real industrial performance. The dataset is synthetic and the model may fail on changing equipment, sensors, and maintenance practices. No temporal or machine-level holdout is possible from the supplied identifiers. Future operational use needs a genuine time-aware evaluation and human review of false negatives and false alarms.

## Reproducibility

- Repository HEAD when the run started: `7dff92752e9e26fffa0f540ee670fb4de17c7f8b`. The training script was uncommitted at that instant; its finalized version is in the subsequent Phase 4 commit. The MLflow run records the observed experiment, and the Git commit records the reproducible implementation.
- Split manifest SHA-256: `7a1fdd0cca26b328c176d621dd96ed62c19fa6a69ca95cb3f8ae492e781bd08a`.
- Selected MLflow run: `e5260d1c99b046f79795c53a4c392575`.
- Separate validation-only MLflow run: `71c564ba12294121ab1e4f78e8eeab9e`, marked FINISHED and tagged with clean Git commit `91f9214f884fe9c2ad665c759d62abe8b4924b7b`. This verifies the committed data-validation entry point; it does **not** replace or retrospectively alter the selected training run.
- Probability model URI: `runs:/e5260d1c99b046f79795c53a4c392575/serving_model`.
- Full candidate metrics, run IDs, threshold policy, and selected result: `reports/model_evaluation.json`.

The selected MLflow model includes the scikit-learn preprocessing pipeline. The seven input columns are required; FastAPI derives the temperature gap from the six user-provided fields. At the chosen threshold, the model emits a positive alert when failure probability is at least 0.37.
