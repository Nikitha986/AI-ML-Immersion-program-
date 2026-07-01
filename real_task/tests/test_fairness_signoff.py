import json
import tempfile
import unittest
from pathlib import Path

from matching.fairness_audit import run_fairness_audit, sign_off_model


class FairnessSignoffTests(unittest.TestCase):
    def test_sign_off_model_persists_approval_state(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            signoff_path = Path(tmp_dir) / "signoff.json"
            audit = run_fairness_audit()
            result = sign_off_model(
                audit=audit,
                reviewer="founder",
                decision="approve",
                signoff_path=str(signoff_path),
            )
            self.assertTrue(result["signed_off"])
            self.assertEqual(result["reviewer"], "founder")
            self.assertEqual(result["decision"], "approve")
            persisted = json.loads(signoff_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["decision"], "approve")


if __name__ == "__main__":
    unittest.main()
