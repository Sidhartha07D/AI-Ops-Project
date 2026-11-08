"""Write a verified candidate manifest without changing the active release."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.artifacts import tree_digest, load_model

root = Path(__file__).resolve().parents[1]
record = json.loads((root/"reports/pipeline_evaluation.json").read_text())
assert record["test_rows_used"] == 0
assert tree_digest(root/record["model_path"]) == record["artifact_sha256"]
load_model(root/record["model_path"])
manifest = {key:record[key] for key in ["run_id","git_sha","model_path","artifact_sha256","split_manifest_sha256","threshold","release_eligible"]}
manifest["deployment"] = "not activated; explicit operator gate required"
(root/"reports/candidate_release.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
