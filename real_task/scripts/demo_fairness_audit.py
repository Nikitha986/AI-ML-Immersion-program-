import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from matching.fairness_audit import run_fairness_audit, save_fairness_audit


audit = run_fairness_audit()
print(audit)
save_fairness_audit()
