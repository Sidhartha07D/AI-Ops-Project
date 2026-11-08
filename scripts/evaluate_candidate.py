"""Verify content identity and evaluate only the fixed validation partition."""

import json
import sys
from hashlib import sha256
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score, recall_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.train_models import FEATURES, ROOT
from scripts.artifacts import load_model, tree_digest


def main():
    record = json.loads((ROOT / "reports/pipeline_training.json").read_text())
    path = ROOT / record["model_path"]
    assert tree_digest(path) == record["artifact_sha256"], "Artifact identity changed"
    source = ROOT / "data/processed/spark_features.csv"
    split = ROOT / "data/splits/split_ids.csv"
    assert sha256(source.read_bytes()).hexdigest() == record["data_sha256"]
    assert sha256(split.read_bytes()).hexdigest() == record["split_manifest_sha256"]
    frame = pd.read_csv(source).merge(
        pd.read_csv(split), on="udi", validate="one_to_one"
    )
    validation = frame.loc[frame.split == "validation"]
    assert len(validation) == 2000
    model = load_model(path)
    probability = np.asarray(model.predict(validation[FEATURES]))[:, 1]
    assert (
        np.isfinite(probability).all()
        and ((0 <= probability) & (probability <= 1)).all()
    )
    result = {
        **record,
        "validation_rows": len(validation),
        "validation_average_precision": float(
            average_precision_score(validation.machine_failure, probability)
        ),
        "validation_recall_at_champion_threshold": float(
            recall_score(validation.machine_failure, probability >= record["threshold"])
        ),
    }
    baseline = json.loads((ROOT / "reports/model_evaluation.json").read_text())
    result["release_eligible"] = bool(
        result["validation_average_precision"] + 1e-9
        >= baseline["selected_validation"]["average_precision"]
        and result["validation_recall_at_champion_threshold"] + 1e-9
        >= baseline["selected_validation"]["recall"]
    )
    # Global sensitivity on validation data; correlated inputs limit attribution.
    from mlflow.sklearn import load_model as load_sklearn

    fitted = load_sklearn(str(path))
    importance = permutation_importance(
        fitted,
        validation[FEATURES],
        validation.machine_failure,
        scoring="average_precision",
        n_repeats=3,
        random_state=42,
        n_jobs=1,
    )
    result["permutation_importance_ap_drop"] = dict(
        zip(FEATURES, map(float, importance.importances_mean))
    )
    result["interpretation"] = (
        "Validation-only model score; not calibrated field failure probability. Importance is not causal."
    )
    (ROOT / "reports/pipeline_evaluation.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    mlflow.set_tracking_uri("sqlite:///" + str(ROOT / "mlflow_store/mlflow.db"))
    with mlflow.start_run(run_id=record["run_id"]):
        mlflow.log_metrics(
            {
                k: result[k]
                for k in [
                    "validation_average_precision",
                    "validation_recall_at_champion_threshold",
                ]
            }
        )
        mlflow.log_dict(result, "validation_evaluation.json")
    print(
        "Validation evaluation:",
        result["validation_average_precision"],
        "eligible:",
        result["release_eligible"],
        "locked-test rows scored: 0",
    )


if __name__ == "__main__":
    main()
