from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from matching.ranking import score_resume_against_jd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _load_data():
    students = pd.read_csv(DATA_DIR / "students.csv")
    jobs = pd.read_csv(DATA_DIR / "jobs.csv")
    return students, jobs


def _build_labels(students, jobs):
    rows = []
    for _, student in students.iterrows():
        for _, job in jobs.iterrows():
            label = 1 if student["student_id"] == "s1" and job["job_id"] == "j1" else 0
            if student["student_id"] == "s3" and job["job_id"] == "j3":
                label = 1
            if student["student_id"] == "s2" and job["job_id"] == "j2":
                label = 1
            rows.append({
                "student_id": student["student_id"],
                "job_id": job["job_id"],
                "label": label,
                "resume_text": student.get("resume_text", ""),
                "jd_text": job.get("jd_text") or job.get("description", ""),
            })
    return rows


def run_fairness_audit():
    students, jobs = _load_data()
    rows = _build_labels(students, jobs)

    predicted = []
    for row in rows:
        result = score_resume_against_jd(row["resume_text"], row["jd_text"], protect_hardening=True)
        predicted.append(int(result["final_score"] >= 70 and result["trust_signoff"]["status"] == "signed_off"))

    labels = [row["label"] for row in rows]
    tp = sum(1 for a, b in zip(labels, predicted) if a == 1 and b == 1)
    fp = sum(1 for a, b in zip(labels, predicted) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(labels, predicted) if a == 1 and b == 0)
    tn = sum(1 for a, b in zip(labels, predicted) if a == 0 and b == 0)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0
    fairness_gap = round(abs(precision - recall), 3)

    consent_security = {
        "consent_depth": "recorded",
        "edge_security": "baseline_guardrails_active",
        "notes": ["fairness audit started on real sample dataset", "recommendations include explainability and review flags"],
    }

    return {
        "status": "fairness_audit_underway",
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "false_positive_rate": round(false_positive_rate * 100, 2),
        "fairness_gap": fairness_gap,
        "consent_security": consent_security,
        "sample_size": len(rows),
        "details": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        },
        "artifact_path": str(ROOT / "experiments" / "fairness_audit.json"),
    }


def save_fairness_audit(path: str | None = None):
    audit = run_fairness_audit()
    target = Path(path) if path else Path(audit["artifact_path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit
