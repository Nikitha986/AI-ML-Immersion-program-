Monetization Quality Sign-off
===========================

Date: 2026-06-23

Scope
-----
Confirm that monetization changes (conversion/paid-apply uplift) did not degrade matching relevance.

What was run
------------
- `scripts/check_conversion_quality.py` — computes per-job Spearman rank correlation between rankings before and after conversion tuning and writes `experiments/conversion_quality.csv`.
- `scripts/spend_reconciliation.py` — lists paid applies and whether they triggered a low-fit warning, writes `experiments/spend_quality.csv`.

Key metrics
-----------
- Average Spearman rho: 1.0000
- Jobs failing threshold (rho >= 0.80): 0/3
- Paid candidates moved into top‑3 (total across jobs): 0

Files produced / artifacts
-------------------------
- experiments/conversion_quality.csv
- experiments/spend_quality.csv

Conclusion
----------
No relevance regression detected — PASS. Under the tested dataset and configuration (conversion_boost=0.12, protect_conversion=True), monetization uplift did not degrade matching quality.

Recommended next steps
----------------------
- Run the same checks on larger or production-like datasets and add Kendall tau and precision@k for broader assurance.
- Add a scheduled CI job to run `scripts/check_conversion_quality.py` and fail the build if rho drops below the configured threshold.

Signed-off-by: automation
