"""Fit a validation-only candidate; never read or score the locked test split."""

import argparse
import json
import shutil
import sys
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import average_precision_score, recall_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.train_models import FEATURES, ROOT, SEED, make_pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", choices=["random_forest_balanced", "hist_gradient_boosting"])
    args = parser.parse_args()
    data = pd.read_csv(ROOT / "data/processed/spark_features.csv")
    split = pd.read_csv(ROOT / "data/splits/split_ids.csv")
    summary = json.loads((ROOT / "reports/split_summary.json").read_text())
    baseline = json.loads((ROOT / "reports/model_evaluation.json").read_text())
    joined = data.merge(split, on="udi", validate="one_to_one")
    train = joined.loc[joined.split == "train"]
    validation = joined.loc[joined.split == "validation"]
    assert len(train) == 6000 and len(validation) == 2000
    # The test rows are never selected or passed to this script's model.
    estimator = (RandomForestClassifier(n_estimators=80, max_depth=8, min_samples_leaf=3, class_weight="balanced_subsample", random_state=SEED, n_jobs=2)
                 if args.name == "random_forest_balanced" else HistGradientBoostingClassifier(max_iter=80, max_depth=6, random_state=SEED))
    model = make_pipeline(estimator)
    model.fit(train[FEATURES], train.machine_failure)
    probability = model.predict_proba(validation[FEATURES])[:, 1]
    threshold = baseline["selected_threshold"]
    report = {
        "candidate": args.name,
        "validation_average_precision": float(average_precision_score(validation.machine_failure, probability)),
        "validation_recall_at_champion_threshold": float(recall_score(validation.machine_failure, probability >= threshold)),
        "threshold": threshold,
        "train_rows": len(train), "validation_rows": len(validation), "test_rows_used": 0,
        "split_manifest_sha256": summary["manifest_sha256"], "feature_columns": FEATURES,
    }
    store = ROOT / "mlflow_store"
    mlflow.set_tracking_uri("sqlite:///" + str(store / "mlflow.db"))
    mlflow.set_experiment("smart-maintenance-operations")
    with mlflow.start_run(run_name=f"retrain_{args.name}") as run:
        mlflow.set_tags({"stage": "validation_only_retrain", "candidate": args.name, "split_manifest_sha256": summary["manifest_sha256"], "locked_test_used": "false"})
        mlflow.log_params({"estimator": args.name, "train_rows": len(train), "validation_rows": len(validation), "threshold": threshold})
        mlflow.log_metrics({"validation_average_precision": report["validation_average_precision"], "validation_recall_at_champion_threshold": report["validation_recall_at_champion_threshold"]})
        signature = infer_signature(train[FEATURES].head(5), model.predict_proba(train[FEATURES].head(5)))
        trusted = (["numpy.dtype", "sklearn.tree._tree.Tree"] if args.name == "random_forest_balanced"
                   else ["numpy.dtype", "sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"])
        mlflow.sklearn.log_model(model, name="candidate_model", signature=signature, input_example=train[FEATURES].head(3), pyfunc_predict_fn="predict_proba", skops_trusted_types=trusted)
        report["run_id"] = run.info.run_id
        report["model_uri"] = f"runs:/{run.info.run_id}/candidate_model"
    candidate_dir = ROOT / "models" / f"candidate_{args.name}"
    downloaded = Path(mlflow.artifacts.download_artifacts(artifact_uri=report["model_uri"], dst_path=str(ROOT / "models" / "downloads")))
    if candidate_dir.exists():
        shutil.rmtree(candidate_dir)
    shutil.copytree(downloaded, candidate_dir)
    report["model_path"] = str(candidate_dir.relative_to(ROOT))
    reports = ROOT / "reports/retrain_candidates"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"{args.name}.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
