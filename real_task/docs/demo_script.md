# 2-minute demo script & verification checklist

Goal: Show end-to-end matching for one student ↔ one job and surface explainability and metrics.

Steps (2 minutes)
- Start server: `python -m uvicorn api.server:app --reload --port 8000` (30s)
- Run test script: PowerShell `scripts\test_api.ps1` (20s)
- Show `experiments/baseline_metrics.csv` in a viewer; point out precision/recall/fpr for chosen threshold (30s)
- Walk through the explainable example printed by `evaluate_baseline.py`: show matched skills and the plain-English reasons (30s)

Verification checklist
- [ ] API responds to `POST /match_text` with JSON containing `final_score` and `matched_skills`.
- [ ] `POST /rank_job` returns a `candidates` list sorted by `match_score`.
- [ ] `experiments/baseline_metrics.csv` exists and contains metrics for train/val/test.
- [ ] Explainable example shows which features (skills, cgpa, experience) contributed to the score.

Notes
- If running on a different host/port, update `scripts/test_api.ps1` base URL.
- For a real demo, replace synthetic texts with an actual resume + JD and show the `reasons` and `matched_skills` fields.
