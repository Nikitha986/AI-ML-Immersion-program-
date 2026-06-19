# Demo and verification steps

Run the baseline evaluation (produces `experiments/baseline_metrics.csv` and an explainable example):

```bash
python experiments/evaluate_baseline.py
```

Start the API server (development):

```bash
uvicorn api.server:app --reload --port 8000
```

Endpoints:
- `POST /match_text` with JSON `{ "resume_text": "...", "jd_text": "..." }`
- `POST /rank_job` with JSON `{ "job_id": "J001" }`
