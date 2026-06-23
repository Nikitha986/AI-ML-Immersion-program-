import random
from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from baseline.matching import _load_data, calculate_match
from matching.ranking import score_resume_against_jd


def run_ab_experiment(pay_fraction=0.2, boost=10.0, thresholds=(50, 60, 65, 70, 80)):
    """Simulate an A/B test where a fraction of candidates 'pay' and receive a score boost.

    - pay_fraction: proportion of candidates that pay in treatment
    - boost: additive score boost applied to paid candidates in the treatment arm
    """
    students, jobs = _load_data()

    # Build all pairs
    pairs = []
    for _, s in students.iterrows():
        for _, j in jobs.iterrows():
            pairs.append((s["student_id"], j["job_id"]))

    records_control = []
    records_treatment = []

    # Assign paid status per student (globally for experiment)
    paid_students = set(random.sample(list(students["student_id"]), k=max(1, int(len(students) * pay_fraction))))

    for sid, jid in pairs:
        res = calculate_match(sid, jid)
        # control uses baseline score
        records_control.append({
            "student_id": sid,
            "job_id": jid,
            "match_score": res["match_score"]
        })

        # treatment: if student paid, apply boost to match_score
        treated_score = res["match_score"] + (boost if sid in paid_students else 0.0)
        records_treatment.append({
            "student_id": sid,
            "job_id": jid,
            "match_score": treated_score,
            "paid": sid in paid_students
        })

    df_control = pd.DataFrame(records_control)
    df_treatment = pd.DataFrame(records_treatment)

    # Load labels if present, otherwise synthesize as before
    data_dir = Path(__file__).resolve().parents[1] / "data"
    labels_path = data_dir / "labels.csv"
    if labels_path.exists():
        labels = pd.read_csv(labels_path)
        df_control = df_control.merge(labels, on=["student_id", "job_id"], how="left")
        df_treatment = df_treatment.merge(labels, on=["student_id", "job_id"], how="left")
        # ensure unified label column name when merges create suffixes
        if "label" not in df_control.columns:
            if "label_y" in df_control.columns:
                df_control["label"] = df_control["label_y"].fillna(0).astype(int)
            elif "label_x" in df_control.columns:
                df_control["label"] = df_control["label_x"].fillna(0).astype(int)

        if "label" not in df_treatment.columns:
            if "label_y" in df_treatment.columns:
                df_treatment["label"] = df_treatment["label_y"].fillna(0).astype(int)
            elif "label_x" in df_treatment.columns:
                df_treatment["label"] = df_treatment["label_x"].fillna(0).astype(int)
    else:
        df_control["label"] = (df_control["match_score"] >= 65).astype(int)
        df_treatment["label"] = (df_treatment["match_score"] >= 65).astype(int)

    results = []
    for name, df in [("control", df_control), ("treatment", df_treatment)]:
        for thr in thresholds:
            y_true = df["label"].values
            y_pred = (df["match_score"] >= thr).astype(int).values

            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            results.append({
                "arm": name,
                "threshold": thr,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "fpr": round(fpr, 4),
                "support": int(y_true.sum())
            })

    out_dir = Path(__file__).resolve().parents[1] / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ab_results.csv"
    pd.DataFrame(results).to_csv(out_path, index=False)

    print(f"Saved A/B results to {out_path}")


if __name__ == "__main__":
    run_ab_experiment()
