import unittest

from matching.fairness_audit import run_fairness_audit


class FairnessAuditTests(unittest.TestCase):
    def test_audit_returns_demoable_metrics(self):
        audit = run_fairness_audit()
        self.assertIn("precision", audit)
        self.assertIn("recall", audit)
        self.assertIn("false_positive_rate", audit)
        self.assertIn("fairness_gap", audit)
        self.assertIn("status", audit)
        self.assertIn("consent_security", audit)


if __name__ == "__main__":
    unittest.main()
