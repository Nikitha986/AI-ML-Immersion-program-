from parsing.resume_parser import parse_resume
from parsing.jd_parser import parse_jd
from matching.rule_matcher import rule_match
from matching.semantic_matcher import semantic_match

def rank_candidate(resume_text, jd_text):
    """Backward-compatible wrapper that scores a single resume vs a JD.

    Returns the same payload shape as before but delegates to the
    internal scoring helper so explainability fields are available.
    """
    return score_resume_against_jd(resume_text, jd_text)


def score_resume_against_jd(resume_text, jd_text, weights=(0.7, 0.3)):
    """Score a resume against a job description and return explainable payload.

    weights: tuple(rule_weight, semantic_weight)
    """
    resume = parse_resume(resume_text)
    jd = parse_jd(jd_text)

    rule_result = rule_match(
        resume.get("skills", []),
        jd.get("required_skills", [])
    )

    semantic_score = semantic_match(resume_text, jd_text)

    rule_w, sem_w = weights
    final_score = (rule_result["match_score"] * rule_w + semantic_score * sem_w)

    recommendation = "Strong Match"
    if final_score < 80:
        recommendation = "Moderate Match"
    if final_score < 60:
        recommendation = "Weak Match"

    reasons = []
    if rule_result.get("matched_skills"):
        reasons.append("matched_skills: " + ", ".join(rule_result["matched_skills"]))
    if rule_result.get("missing_skills"):
        reasons.append("missing_skills: " + ", ".join(rule_result["missing_skills"]))
    reasons.append(f"semantic_score: {semantic_score}")

    return {
        "final_score": round(final_score, 2),
        "recommendation": recommendation,
        "matched_skills": rule_result.get("matched_skills", []),
        "missing_skills": rule_result.get("missing_skills", []),
        "semantic_score": semantic_score,
        "reasons": reasons
    }


def rank_jobs_for_student(resume_text, jobs, top_k=None, weights=(0.7, 0.3)):
    """Rank a list of jobs for a single student/resume.

    jobs: iterable of dict-like objects with at least `job_id` and `jd_text` keys.
    Returns a list of ranked job payloads sorted by `final_score` desc.
    """
    scored = []
    for job in jobs:
        job_id = job.get("job_id")
        jd_text = job.get("jd_text") or job.get("description") or job.get("jd")
        if jd_text is None:
            continue

        res = score_resume_against_jd(resume_text, jd_text, weights=weights)
        res["job_id"] = job_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored


def rank_candidates_for_job(jd_text, candidates, top_k=None, weights=(0.7, 0.3)):
    """Rank a list of candidate resumes for a given job description.

    candidates: iterable of dict-like objects with at least `candidate_id` and `resume_text` keys.
    Returns a list of ranked candidate payloads sorted by `final_score` desc.
    """
    scored = []
    for c in candidates:
        candidate_id = c.get("candidate_id") or c.get("id")
        resume_text = c.get("resume_text") or c.get("resume")
        if resume_text is None:
            continue

        res = score_resume_against_jd(resume_text, jd_text, weights=weights)
        res["candidate_id"] = candidate_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored