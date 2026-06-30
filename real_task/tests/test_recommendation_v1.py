import unittest

from matching.ranking import score_resume_against_jd


class RecommendationV1Tests(unittest.TestCase):
    def test_strong_match_is_signed_off(self):
        result = score_resume_against_jd(
            "Python SQL TensorFlow AWS",
            "Python SQL TensorFlow AWS",
            protect_hardening=True,
        )
        self.assertEqual(result["trust_signoff"]["status"], "signed_off")
        self.assertFalse(result["admin_flags"]["weak_item_flag"])

    def test_weak_match_needs_review(self):
        result = score_resume_against_jd(
            "Java only",
            "Python TensorFlow AWS",
            protect_hardening=True,
        )
        self.assertEqual(result["trust_signoff"]["status"], "needs_review")
        self.assertTrue(result["admin_flags"]["weak_item_flag"])


if __name__ == "__main__":
    unittest.main()
