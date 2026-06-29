"""Evaluate false-positive reduction for proctoring hardening.

This script computes baseline and hardening scores for all student-job
tuples, then compares false positive rates (FPR) against the labeled ground
truth in data/labels.csv.
"""

import os
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from baseline.matching import _load_data, calculate_match
from matching.ranking import score_resume_against_jd


def compute_metrics(df, threshold=65):
    df = df.copy()
    df["predicted_label"] = (df["score"] >= threshold).astype(int)
    y_true = df["label"].values
    y_pred = df["predicted_label"].values

    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4),
    }


def main(threshold=65, hardening_boost=0.1):
    students, jobs = _load_data()
    label_path = Path(__file__).resolve().parents[1] / "data" / "labels.csv"
    if not label_path.exists():
        raise FileNotFoundError("Expected data/labels.csv for FP evaluation.")

    labels = pd.read_csv(label_path)

    records = []
    for _, s in students.iterrows():
        for _, j in jobs.iterrows():
            sid = s["student_id"]
            jid = j["job_id"]
            baseline = calculate_match(sid, jid)
            hardening = score_resume_against_jd(
                s.get("resume_text", ""),
                j.get("description", ""),
                protect_hardening=True,
                hardening_boost=hardening_boost,
            )

            label_row = labels[(labels["student_id"] == sid) & (labels["job_id"] == jid)]
            if label_row.empty:
                continue
            label = int(label_row.iloc[0]["label"])

            records.append({
                "student_id": sid,
                "job_id": jid,
                "label": label,
                "baseline_score": baseline["match_score"],
                "hardening_score": hardening["final_score"],
            })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No labeled pairs found for evaluation.")

    baseline_metrics = compute_metrics(df[["label", "baseline_score"]].rename(columns={"baseline_score": "score"}), threshold)
    hardening_metrics = compute_metrics(df[["label", "hardening_score"]].rename(columns={"hardening_score": "score"}), threshold)

    out_dir = Path(__file__).resolve().parents[1] / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fp_reduction.csv"

    df.to_csv(out_path, index=False)

    print("False-positive reduction evaluation")
    print("Threshold:", threshold)
    print("Baseline:", baseline_metrics)
    print("Hardening:", hardening_metrics)
    print("Saved detailed pair scores to", out_path)

    return baseline_metrics, hardening_metrics


if __name__ == "__main__":
    main()
