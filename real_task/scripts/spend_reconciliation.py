"""Generate a spend-quality reconciliation report for paid applies.

Writes `experiments/spend_quality.csv` listing paid (candidate,job)
pairs and whether they triggered a low-fit warning.
"""
import csv
from baseline.matching import _load_data
from payments.stub import is_paid
from matching.ranking import rank_candidates_for_job


def main(job_id=None):
    students, jobs = _load_data()

    if job_id is None:
        job_id = jobs.iloc[0]["job_id"]

    jrow = jobs[jobs["job_id"] == job_id]
    if jrow.empty:
        print("job not found")
        return

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    candidates = []
    for _, s in students.iterrows():
        cid = s["student_id"]
        candidates.append({"candidate_id": cid, "resume_text": s.get("resume_text", "")})

    # run ranking with conversion protection to ensure low_fit_warning evaluated
    results = rank_candidates_for_job(jd_text, candidates, protect_conversion=True, conversion_boost=0.12, job_id=job_id)

    out = []
    for r in results:
        cid = r.get("candidate_id")
        paid = is_paid(cid, job_id)
        if paid:
            out.append({
                "candidate_id": cid,
                "job_id": job_id,
                "final_score": r.get("final_score"),
                "low_fit_warning": r.get("low_fit_warning", False)
            })

    out_path = "experiments/spend_quality.csv"
    with open(out_path, "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "job_id", "final_score", "low_fit_warning"])
        for row in out:
            w.writerow([row["candidate_id"], row["job_id"], row["final_score"], row["low_fit_warning"]])

    print(f"Wrote {len(out)} paid rows to {out_path}")


if __name__ == "__main__":
    main()
