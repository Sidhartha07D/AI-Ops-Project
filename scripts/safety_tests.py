"""Failure-path tests with isolated storage and mocked process control."""

import fcntl
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api import main as api
from scripts import release_gate as gate


class SafetyTests(unittest.TestCase):
    def test_frozen_test_entrypoint_refuses_repeat(self):
        from src import train_models

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "reports").mkdir()
            (root / "reports/model_evaluation.json").write_text("{}")
            with patch.object(train_models, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "already been evaluated"):
                    train_models.main()

    def test_storage_failure_is_controlled(self):
        with patch("pathlib.Path.open", side_effect=OSError("fixture disk error")):
            with self.assertRaises(HTTPException) as error:
                api.append_jsonl(Path("/tmp/smm-test-log"), {})
        self.assertEqual(error.exception.status_code, 503)

    def test_unknown_prediction_feedback_rejected(self):
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(api, "OBSERVATIONS", Path(d) / "absent"),
        ):
            with self.assertRaises(HTTPException) as error:
                api.feedback(api.Feedback(prediction_id="unknown-record"))
        self.assertEqual(error.exception.status_code, 404)

    def test_release_lock_blocks_predictions(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "models").mkdir()
            with (
                patch.object(api, "ROOT", root),
                (root / "models/.release.lock").open("a") as lock,
            ):
                fcntl.flock(lock, fcntl.LOCK_EX)
                with self.assertRaises(HTTPException) as error:
                    with api.release_read_lock():
                        self.fail("Lock was bypassed")
                self.assertEqual(error.exception.status_code, 503)
                with patch.object(api, "fetch_model") as model:
                    self.assertEqual(api.health()["model"], "unavailable")
                    model.assert_not_called()

    def test_failed_switch_restores_bytes_and_policy(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            models = root / "models"
            models.mkdir()
            active = models / "active"
            active.mkdir()
            (active / "MLmodel").write_text("original")
            candidate = models / "candidate"
            candidate.mkdir()
            (candidate / "MLmodel").write_text("candidate")
            release = models / "active_release.json"
            old = {
                "run_id": "original",
                "model_path": "models/active",
                "threshold": 0.37,
            }
            release.write_text(json.dumps(old))
            with (
                patch.multiple(
                    gate,
                    ROOT=root,
                    MODELS=models,
                    ACTIVE=active,
                    RELEASE=release,
                    EVENTS=root / "events.jsonl",
                ),
                patch.object(gate, "load_model"),
                patch.object(gate.subprocess, "run"),
                patch.object(
                    gate,
                    "restart_and_check",
                    side_effect=[RuntimeError("injected failed restart"), None],
                ) as restart,
            ):
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    gate.switch_release(
                        {
                            "run_id": "new",
                            "model_path": "models/candidate",
                            "threshold": 0.4,
                        }
                    )
                self.assertEqual((active / "MLmodel").read_text(), "original")
                self.assertEqual(json.loads(release.read_text()), old)
                self.assertEqual(restart.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
