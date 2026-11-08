"""Focused API tests that run without starting the model server."""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.main import Reading, predict


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.reading = Reading(
            type="M", air_temperature_k=298.1, process_temperature_k=308.6,
            rotational_speed_rpm=1551, torque_nm=42.8, tool_wear_min=0,
        )

    def test_feature_mapping_and_routine_recommendation(self):
        with patch("api.main.fetch_model", return_value={"predictions": [[0.9, 0.1]]}) as model:
            result = predict(self.reading)
        self.assertEqual(model.call_args.args[1]["dataframe_records"][0]["temperature_gap_k"], 10.5)
        self.assertFalse(result["alert"])
        self.assertEqual(result["recommendation"], "Continue routine checks")

    def test_threshold_boundary_flags_inspection(self):
        with patch("api.main.fetch_model", return_value={"predictions": [[0.63, 0.37]]}):
            result = predict(self.reading)
        self.assertTrue(result["alert"])
        self.assertEqual(result["recommendation"], "Schedule an inspection")

    def test_invalid_reading_is_rejected(self):
        with self.assertRaises(ValidationError):
            Reading.model_validate({**self.reading.model_dump(), "rotational_speed_rpm": -1})

    def test_bad_model_response_is_reported(self):
        with patch("api.main.fetch_model", return_value={"predictions": []}):
            with self.assertRaises(HTTPException) as raised:
                predict(self.reading)
        self.assertEqual(raised.exception.status_code, 502)

    def test_non_finite_probability_is_rejected(self):
        with patch("api.main.fetch_model", return_value={"predictions": [[0.0, float("nan")]]}):
            with self.assertRaises(HTTPException) as raised:
                predict(self.reading)
        self.assertEqual(raised.exception.status_code, 502)

    def test_unavailable_model_is_reported(self):
        with patch("api.main.fetch_model", side_effect=HTTPException(status_code=503, detail="unavailable")):
            with self.assertRaises(HTTPException) as raised:
                predict(self.reading)
        self.assertEqual(raised.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main(verbosity=2)
