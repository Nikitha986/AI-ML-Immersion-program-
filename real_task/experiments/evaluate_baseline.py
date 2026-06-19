import os
from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]

from baseline.matching import calculate_match


def build_pairs(students_df, jobs_df):
    pairs = []
    for _, s in students_df.iterrows():
        for _, j in jobs_df.iterrows():
            pairs.append((s["student_id"], j["job_id"]))
    return pairs


def evaluate(thresholds=(50, 60, 65, 70, 80)):
    data_dir = ROOT / "data"
    students = pd.read_csv(data_dir / "students.csv")
    jobs = pd.read_csv(data_dir / "jobs.csv")

    pairs = build_pairs(students, jobs)

    records = []

    # compute baseline scores for every pair
    for sid, jid in pairs:
        res = calculate_match(sid, jid)
        records.append({
            "student_id": sid,
            "job_id": jid,
            "match_score": res["match_score"],
            "recommendation": res["recommendation"],
            "reasons": "; ".join(res.get("reasons", []))
        })

    df = pd.DataFrame(records)

    # load labels if provided, otherwise synthesize simple labels for demo
    labels_path = data_dir / "labels.csv"
    if labels_path.exists():
        labels = pd.read_csv(labels_path)
        df = df.merge(labels, on=["student_id", "job_id"], how="left")
    else:
        # Pseudo ground-truth for demo: treat scores >= 65 as positive
        df["label"] = (df["match_score"] >= 65).astype(int)

    # train/val/test split on the candidate pairs
    try:
        train, test = train_test_split(df, test_size=0.4, random_state=42, stratify=df["label"])
        val, test = train_test_split(test, test_size=0.5, random_state=42, stratify=test["label"])
    except ValueError:
        # fallback for very small datasets where stratify is not possible
        train, test = train_test_split(df, test_size=0.4, random_state=42)
        val, test = train_test_split(test, test_size=0.5, random_state=42)

    results = []

    for split_name, split_df in [("train", train), ("val", val), ("test", test)]:
        for thr in thresholds:
            y_true = split_df["label"].values
            y_pred = (split_df["match_score"] >= thr).astype(int).values

            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            results.append({
                "split": split_name,
                "threshold": thr,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "fpr": round(fpr, 4),
                "support": int(y_true.sum())
            })

    out_dir = ROOT / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(out_dir / "baseline_metrics.csv", index=False)

    # demo: print one explainable walkthrough (top candidate for first job)
    first_job = jobs.iloc[0]["job_id"]
    job_candidates = df[df["job_id"] == first_job].sort_values("match_score", ascending=False)
    top = job_candidates.iloc[0]

    print("Explainable example for job", first_job)
    print(top.to_dict())
    print("Saved metrics to experiments/baseline_metrics.csv")


if __name__ == "__main__":
    evaluate()
