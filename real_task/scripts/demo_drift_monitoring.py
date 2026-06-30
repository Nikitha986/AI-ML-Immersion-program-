import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from matching.drift_monitoring import run_drift_monitoring, save_drift_monitoring

payload = run_drift_monitoring()
print(payload)
save_drift_monitoring()
