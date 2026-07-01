import json
import tempfile
import unittest
from pathlib import Path

from matching.mlops_foundation import build_feature_store, register_model, run_mlops_foundation


class MLOpsFoundationTests(unittest.TestCase):
    def test_feature_store_builds_demoable_rows(self):
        features = build_feature_store()
        self.assertGreaterEqual(len(features), 3)
        self.assertIn("student_id", features[0])
        self.assertIn("job_id", features[0])
        self.assertIn("final_score", features[0])

    def test_registry_registration_persists_model_entry(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_path = Path(tmp_dir) / "registry.json"
            entry = register_model(
                model_name="place-mux-ranker",
                version="v1.0",
                status="staged",
                metrics={"precision": 83.2, "recall": 78.4},
                registry_path=str(registry_path),
            )
            self.assertEqual(entry["model_name"], "place-mux-ranker")
            self.assertEqual(entry["version"], "v1.0")
            persisted = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(persisted), 1)

    def test_run_mlops_foundation_returns_registry_and_feature_store(self):
        result = run_mlops_foundation()
        self.assertEqual(result["status"], "mlops_foundation_live")
        self.assertIn("registry", result)
        self.assertIn("feature_store", result)
        self.assertTrue(result["registry"]["ready"])
        self.assertTrue(result["feature_store"]["ready"])


if __name__ == "__main__":
    unittest.main()
