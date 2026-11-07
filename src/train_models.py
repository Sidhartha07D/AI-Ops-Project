"""Train small, reproducible baselines and record a single locked-test evaluation."""

from __future__ import annotations

import json
import os
import subprocess
from hashlib import sha256
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["type", "air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min", "temperature_gap_k"]
NUMERIC = FEATURES[1:]
SEED = 42


def metrics(y: pd.Series, probability: np.ndarray, threshold: float) -> dict:
    prediction = (probability >= threshold).astype(int)
    return {
        "average_precision": float(average_precision_score(y, probability)),
        "roc_auc": float(roc_auc_score(y, probability)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "brier": float(brier_score_loss(y, probability)),
        "threshold": float(threshold),
        "positive_count": int(y.sum()),
        "prevalence": float(y.mean()),
        "confusion_matrix": confusion_matrix(y, prediction, labels=[0, 1]).tolist(),
    }


def make_pipeline(estimator) -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            ("type", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), ["type"]),
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ],
        sparse_threshold=0,
    )
    return Pipeline([("preprocess", preprocessor), ("classifier", estimator)])


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> None:
    data = pd.read_csv(ROOT / "data/processed/spark_features.csv")
    ids = pd.read_csv(ROOT / "data/splits/split_ids.csv")
    summary = json.loads((ROOT / "reports/split_summary.json").read_text())
    assert sha256((ROOT / "data/splits/split_ids.csv").read_bytes()).hexdigest() == summary["manifest_sha256"]
    assert ids.udi.is_unique and data.udi.is_unique and len(ids) == len(data) == 10_000
    frame = data.merge(ids, on="udi", validate="one_to_one")
    assert set(frame.split) == {"train", "validation", "test"}
    parts = {name: frame.loc[frame.split == name].copy() for name in ("train", "validation", "test")}
    assert [len(parts[name]) for name in ("train", "validation", "test")] == [6000, 2000, 2000]
    X = {name: part[FEATURES] for name, part in parts.items()}
    y = {name: part.machine_failure for name, part in parts.items()}

    store = ROOT / "mlflow_store"
    store.mkdir(exist_ok=True)
    mlflow.set_tracking_uri((store / "mlflow.db").as_uri().replace("file://", "sqlite:///"))
    experiment = mlflow.get_experiment_by_name("smart-maintenance-baselines")
    if experiment is None:
        experiment_id = mlflow.create_experiment("smart-maintenance-baselines", artifact_location=(store / "artifacts").as_uri())
    else:
        experiment_id = experiment.experiment_id
    mlflow.set_experiment(experiment_id=experiment_id)

    candidates = {
        "dummy_prior": DummyClassifier(strategy="prior"),
        "logistic_balanced": LogisticRegression(class_weight="balanced", max_iter=600, random_state=SEED),
        "random_forest_balanced": RandomForestClassifier(n_estimators=80, max_depth=8, min_samples_leaf=3, class_weight="balanced_subsample", random_state=SEED, n_jobs=2),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=80, max_depth=6, random_state=SEED),
    }
    trained = {}
    results = {}
    run_ids = {}
    provenance = {"git_sha": git_sha(), "split_manifest_sha256": summary["manifest_sha256"], "seed": str(SEED), "data_source": "UCI AI4I 2020", "target": "machine_failure"}
    for name, estimator in candidates.items():
        pipeline = make_pipeline(estimator)
        with mlflow.start_run(run_name=name, nested=True) as run:
            mlflow.set_tags({**provenance, "stage": "validation", "candidate": name})
            mlflow.log_params({"estimator": name, "features": ",".join(FEATURES), "train_rows": len(X["train"]), "validation_rows": len(X["validation"])})
            pipeline.fit(X["train"], y["train"])
            prob = pipeline.predict_proba(X["validation"])[:, 1]
            result = metrics(y["validation"], prob, 0.5)
            mlflow.log_metrics({f"validation_{k}": v for k, v in result.items() if isinstance(v, float)})
            mlflow.log_dict(result, "validation_metrics.json")
            trained[name] = pipeline
            results[name] = result
            run_ids[name] = run.info.run_id
            print(f"{name}: validation AP={result['average_precision']:.4f}, recall@0.5={result['recall']:.4f}", flush=True)

    winner = max(candidates, key=lambda name: (results[name]["average_precision"], name))
    model = trained[winner]
    validation_prob = model.predict_proba(X["validation"])[:, 1]
    threshold_options = np.linspace(0.05, 0.95, 91)
    def f2(t: float) -> float:
        pred = (validation_prob >= t).astype(int)
        p = precision_score(y["validation"], pred, zero_division=0)
        r = recall_score(y["validation"], pred, zero_division=0)
        return float(5 * p * r / (4 * p + r)) if (4 * p + r) else 0.0
    threshold = float(max(threshold_options, key=lambda t: (f2(t), t)))
    validation_final = metrics(y["validation"], validation_prob, threshold)
    test_prob = model.predict_proba(X["test"])[:, 1]
    test = metrics(y["test"], test_prob, threshold)

    report = {"selection_policy": "highest validation average precision; threshold maximizes validation F2 over 0.05..0.95", "winner": winner, "winner_run_id": run_ids[winner], "git_sha": provenance["git_sha"], "split_manifest_sha256": provenance["split_manifest_sha256"], "candidate_run_ids": run_ids, "candidate_validation": results, "selected_threshold": threshold, "selected_validation": validation_final, "locked_test": test, "test_evaluations": 1, "feature_columns": FEATURES}
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    report_path = reports / "model_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(np.asarray(test["confusion_matrix"]), display_labels=["healthy", "failure"]).plot(ax=ax, colorbar=False)
    ax.set_title(f"Locked test: {winner}, threshold {threshold:.2f}")
    fig.tight_layout()
    plot = reports / "figures/test_confusion_matrix.png"
    fig.savefig(plot, dpi=150)
    plt.close(fig)

    with mlflow.start_run(run_name="selected_model_locked_test", nested=True) as run:
        report["selected_run_id"] = run.info.run_id
        report["serving_model_uri"] = f"runs:/{run.info.run_id}/model"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        mlflow.set_tags({**provenance, "stage": "locked_test", "winner": winner, "candidate_run_id": run_ids[winner]})
        mlflow.log_params({"winner": winner, "threshold": threshold, "selection_metric": "validation_average_precision", "threshold_metric": "validation_F2"})
        mlflow.log_metrics({f"test_{k}": v for k, v in test.items() if isinstance(v, float)})
        mlflow.log_metrics({"validation_average_precision": validation_final["average_precision"], "validation_F2": f2(threshold)})
        mlflow.log_artifact(str(report_path))
        mlflow.log_artifact(str(plot))
        mlflow.log_artifact(str(ROOT / "reports/data_audit.json"))
        mlflow.log_artifact(str(ROOT / "reports/split_summary.json"))
        signature = infer_signature(X["train"].head(5), model.predict_proba(X["train"].head(5)))
        mlflow.sklearn.log_model(
            model, name="model", signature=signature,
            input_example=X["train"].head(3),
            pyfunc_predict_fn="predict_proba",
            skops_trusted_types=["numpy.dtype", "sklearn.tree._tree.Tree"],
        )
    print(f"Selected: {winner}, validation AP={validation_final['average_precision']:.4f}, threshold={threshold:.2f}", flush=True)
    print(f"Locked test: AP={test['average_precision']:.4f}, recall={test['recall']:.4f}, precision={test['precision']:.4f}", flush=True)
    print(f"Selected MLflow run: {report['selected_run_id']}", flush=True)
    print("Model training and locked-test evaluation: PASS", flush=True)


if __name__ == "__main__":
    main()
