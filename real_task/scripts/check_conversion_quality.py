"""Check conversion-quality: ensure paywall hasn't skewed relevance.

Computes Spearman rank correlation between rankings before and after
conversion tuning for each job. Writes `experiments/conversion_quality.csv`
and prints a short pass/fail summary.
"""
import csv
from baseline.matching import _load_data
from matching.ranking import rank_candidates_for_job
from payments.stub import is_paid


def spearman_rho(list_a, list_b):
    # both lists are ordered candidate_id lists of same elements
    n = len(list_a)
    if n < 2:
        return 1.0
    rank_a = {cid: i + 1 for i, cid in enumerate(list_a)}
    rank_b = {cid: i + 1 for i, cid in enumerate(list_b)}
    d2 = 0
    for cid in list_a:
        d = rank_a[cid] - rank_b[cid]
        d2 += d * d
    rho = 1.0 - (6.0 * d2) / (n * (n * n - 1))
    return rho


def main(min_pass_rho=0.80):
    students, jobs = _load_data()

    rows = []
    low_count = 0
    rhos = []

    for _, j in jobs.iterrows():
        job_id = j["job_id"]
        jd_text = j.get("jd_text") or j.get("description") or ""

        candidates = []
        for _, s in students.iterrows():
            candidates.append({"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")})

        before = rank_candidates_for_job(jd_text, candidates, protect_conversion=False, job_id=job_id)
        after = rank_candidates_for_job(jd_text, candidates, protect_conversion=True, conversion_boost=0.12, job_id=job_id)

        before_ids = [r.get("candidate_id") for r in before]
        after_ids = [r.get("candidate_id") for r in after]

        # ensure same set
        if set(before_ids) != set(after_ids):
            # fallback: intersect in original order
            common = [c for c in before_ids if c in set(after_ids)]
            before_order = common
            after_order = [c for c in after_ids if c in set(common)]
        else:
            before_order = before_ids
            after_order = after_ids

        rho = spearman_rho(before_order, after_order)
        rhos.append(rho)
        passed = rho >= min_pass_rho
        if not passed:
            low_count += 1

        # count how many paid candidates rose into top-3
        top3_before = set(before_order[:3])
        top3_after = set(after_order[:3])
        paid_increase = 0
        for cid in top3_after:
            if cid not in top3_before and is_paid(cid, job_id):
                paid_increase += 1

        rows.append({"job_id": job_id, "rho": round(rho, 4), "passed": passed, "paid_in_top3_increase": paid_increase})

    out_path = "experiments/conversion_quality.csv"
    with open(out_path, "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["job_id", "rho", "passed", "paid_in_top3_increase"])
        for r in rows:
            w.writerow([r["job_id"], r["rho"], r["passed"], r["paid_in_top3_increase"]])

    avg_rho = sum(rhos) / len(rhos) if rhos else 1.0
    print(f"Average Spearman rho={avg_rho:.4f}; jobs failing threshold={low_count}/{len(rhos)}")
    if low_count == 0 and avg_rho >= min_pass_rho:
        print("No relevance regression detected — PASS")
    else:
        print("Potential relevance regression detected — INVESTIGATE")


if __name__ == "__main__":
    main()
