"""Integration test: mark a candidate paid and observe ranking uplift.

Writes a small CSV `experiments/paid_uplift.csv` with before/after scores
and prints a concise summary to stdout.
"""
import csv
from baseline.matching import _load_data
from payments.stub import mark_paid, reset, is_paid
from matching.ranking import rank_candidates_for_job


def main(job_id=None, candidate_id=None):
    reset()
    students, jobs = _load_data()

    # choose defaults if not provided
    if job_id is None:
        job_id = jobs.iloc[0]["job_id"]
    if candidate_id is None:
        candidate_id = students.iloc[0]["student_id"]

    jrow = jobs[jobs["job_id"] == job_id]
    if jrow.empty:
        print("job not found")
        return

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    candidates = []
    for _, s in students.iterrows():
        candidates.append({"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")})

    before = rank_candidates_for_job(jd_text, candidates, protect_conversion=False, job_id=job_id)

    # mark the candidate paid and re-run with conversion protection on
    mark_paid(candidate_id, job_id)
    after = rank_candidates_for_job(jd_text, candidates, protect_conversion=True, conversion_boost=0.12, job_id=job_id)

    # find the candidate in before/after
    def find_score(lst, cid):
        for i, r in enumerate(lst, 1):
            if r.get("candidate_id") == cid:
                return i, r.get("final_score")
        return None, None

    pos_before, score_before = find_score(before, candidate_id)
    pos_after, score_after = find_score(after, candidate_id)

    print(f"Candidate {candidate_id} for job {job_id}: before pos={pos_before} score={score_before}; after pos={pos_after} score={score_after}; paid={is_paid(candidate_id, job_id)}")

    # write CSV
    out_path = "experiments/paid_uplift.csv"
    with open(out_path, "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "job_id", "pos_before", "score_before", "pos_after", "score_after", "paid"])
        w.writerow([candidate_id, job_id, pos_before or "", score_before or "", pos_after or "", score_after or "", is_paid(candidate_id, job_id)])

    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
