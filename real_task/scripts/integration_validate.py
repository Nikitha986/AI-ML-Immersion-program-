import json
from baseline.matching import _load_data, calculate_match
from matching.ranking import rank_jobs_for_student, rank_candidates_for_job


def validate_end_to_end(top_k=3):
    students, jobs = _load_data()

    # Validate that score_resume_against_jd == calculate_match for pairs
    mismatches = []
    for _, s in students.iterrows():
        resume_text = s.get("resume_text", "")
        # rank jobs for student
        jobs_list = [{"job_id": j["job_id"], "jd_text": j.get("jd_text", j.get("description", ""))} for _, j in jobs.iterrows()]
        ranked = rank_jobs_for_student(resume_text, jobs_list)

        # Check top_k jobs and compare calculate_match
        for entry in ranked[:top_k]:
            jid = entry["job_id"]
            score_payload = calculate_match(s["student_id"], jid)
            if abs(score_payload["match_score"] - entry["final_score"]) > 1e-6:
                mismatches.append({
                    "student_id": s["student_id"],
                    "job_id": jid,
                    "calc_score": score_payload["match_score"],
                    "rank_score": entry["final_score"]
                })

    # Validate candidate ranking for first job
    first_job = jobs.iloc[0]
    jd_text = first_job.get("jd_text", first_job.get("description", ""))
    candidates = [{"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")} for _, s in students.iterrows()]
    ranked_candidates = rank_candidates_for_job(jd_text, candidates)

    results = {
        "mismatches": mismatches,
        "top_candidates_for_first_job": ranked_candidates[:top_k]
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    validate_end_to_end()
