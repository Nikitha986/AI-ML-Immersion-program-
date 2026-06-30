import unittest

from matching.drift_monitoring import run_drift_monitoring


class DriftMonitoringTests(unittest.TestCase):
    def test_drift_monitoring_returns_retraining_signal(self):
        result = run_drift_monitoring()
        self.assertIn("drift_score", result)
        self.assertIn("retraining_needed", result)
        self.assertIn("data_subject_rights", result)
        self.assertIn("resilience", result)


if __name__ == "__main__":
    unittest.main()
