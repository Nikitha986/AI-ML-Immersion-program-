import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from matching.ranking import score_resume_against_jd


cases = [
    ("Strong match", "Python SQL TensorFlow AWS", "Python SQL TensorFlow AWS"),
    ("Weak match", "Java only", "Python TensorFlow AWS"),
]

for label, resume_text, jd_text in cases:
    result = score_resume_against_jd(resume_text, jd_text, protect_hardening=True)
    print(f"=== {label} ===")
    print({k: result[k] for k in ["final_score", "recommendation", "trust_signoff", "admin_flags", "explanation"]})
    print()
