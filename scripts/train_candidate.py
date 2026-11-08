"""DVC/MLproject validation-only training; never score locked-test rows."""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.train_models import FEATURES, ROOT, make_pipeline
from scripts.artifacts import tree_digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="params.yaml")
    parser.add_argument("--name", default="random_forest_balanced", choices=["random_forest_balanced"])
    args = parser.parse_args()
    cfg = yaml.safe_load((ROOT / args.config).read_text())["candidate"]
    if cfg["name"] != args.name:
        raise ValueError("Candidate name must match the versioned configuration")
    dirty = subprocess.check_output(["git", "diff", "HEAD", "--", "src", "scripts", args.config, "MLproject", "environment.yml", "environment.snapshot.yml", "dvc.yaml"], cwd=ROOT, text=True)
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "--", "src", "scripts"], cwd=ROOT, text=True)
    if dirty.strip() or untracked.strip():
        raise RuntimeError("Commit source/config changes before tracked training")
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source = ROOT / "data/processed/spark_features.csv"
    split_path = ROOT / "data/splits/split_ids.csv"
    data = pd.read_csv(source).merge(pd.read_csv(split_path), on="udi", validate="one_to_one")
    train = data.loc[data.split == "train"]
    assert len(train) == 6000
    estimator = RandomForestClassifier(n_estimators=cfg["n_estimators"], max_depth=cfg["max_depth"], min_samples_leaf=cfg["min_samples_leaf"], class_weight="balanced_subsample", random_state=cfg["seed"], n_jobs=2)
    model = make_pipeline(estimator)
    store = ROOT / "mlflow_store"
    store.mkdir(exist_ok=True)
    mlflow.set_tracking_uri("sqlite:///" + str(store / "mlflow.db"))
    mlflow.set_experiment("smart-maintenance-local-pipeline")
    output = ROOT / "models/pipeline_candidate"
    if output.exists():
        shutil.rmtree(output)
    with mlflow.start_run(run_name="local_dvc_candidate", nested=mlflow.active_run() is not None) as run:
        mlflow.set_tags({"git_sha": git_sha, "source_clean": "true", "locked_test_used": "false", "split_sha256": sha256(split_path.read_bytes()).hexdigest(), "python": platform.python_version()})
        mlflow.log_params(cfg)
        mlflow.log_params({"estimator__" + k: str(v) for k,v in estimator.get_params().items()})
        model.fit(train[FEATURES], train.machine_failure)
        signature = infer_signature(train[FEATURES].head(3), model.predict_proba(train[FEATURES].head(3)))
        mlflow.sklearn.save_model(model, str(output), signature=signature, input_example=train[FEATURES].head(3), pyfunc_predict_fn="predict_proba", skops_trusted_types=["numpy.dtype", "sklearn.tree._tree.Tree"], metadata={"run_id": run.info.run_id, "git_sha": git_sha})
        mlflow.log_artifacts(str(output), "candidate_bundle")
        record = {"run_id": run.info.run_id, "git_sha": git_sha, "source_clean": True, "model_path": "models/pipeline_candidate", "artifact_sha256": tree_digest(output), "split_manifest_sha256": sha256(split_path.read_bytes()).hexdigest(), "data_sha256": sha256(source.read_bytes()).hexdigest(), "feature_columns": FEATURES, "threshold": cfg["threshold"], "test_rows_used": 0, "train_rows": len(train)}
        (ROOT / "reports/pipeline_training.json").write_text(json.dumps(record, indent=2) + "\n")
        mlflow.log_dict(record, "training_provenance.json")
    print("Validation-only candidate trained:", record["run_id"], "source", git_sha)


if __name__ == "__main__":
    main()
