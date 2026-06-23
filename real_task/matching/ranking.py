from parsing.resume_parser import parse_resume
from parsing.jd_parser import parse_jd
from matching.rule_matcher import rule_match
from matching.semantic_matcher import semantic_match
from payments.stub import is_paid

# threshold for low-fit warning (percent)
LOW_FIT_THRESHOLD = 60

def rank_candidate(resume_text, jd_text):
    """Backward-compatible wrapper that scores a single resume vs a JD.

    Returns the same payload shape as before but delegates to the
    internal scoring helper so explainability fields are available.
    """
    return score_resume_against_jd(resume_text, jd_text)


def score_resume_against_jd(resume_text, jd_text, weights=(0.7, 0.3), protect_conversion=False, conversion_boost=0.1, candidate_id=None, job_id=None):
    """Score a resume against a job description and return explainable payload.

    weights: tuple(rule_weight, semantic_weight)
    protect_conversion: when True, apply a small boost that favors candidates
        with higher semantic alignment and more matched skills (aimed to
        protect paid-apply conversion). `conversion_boost` is the maximum
        relative uplift applied to the final score (e.g. 0.1 => up to +10%).
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

    # Conversion protection tuning: favor candidates more likely to convert
    # by boosting final_score based on semantic alignment and matched skills.
    if protect_conversion:
        # matched fraction relative to JD required skills (if available)
        jd = parse_jd(jd_text)
        req = jd.get("required_skills") or []
        matched_count = len(rule_result.get("matched_skills", []))
        matched_frac = (matched_count / len(req)) if req else 0

        # conversion signal: combination of semantic alignment and matched fraction
        signal = (semantic_score / 100.0) * matched_frac
        # ensure signal in [0,1]
        signal = max(0.0, min(1.0, signal))

        uplift = conversion_boost * signal
        # if we have payment context, increase uplift for paid applies
        paid_bonus = 0.0
        try:
            if candidate_id and job_id and is_paid(candidate_id, job_id):
                paid_bonus = conversion_boost * 0.5
        except Exception:
            paid_bonus = 0.0

        uplift = min(1.0, uplift + paid_bonus)
        final_score = final_score * (1.0 + uplift)
        reasons.append(f"conversion_tuning_applied: uplift={round(uplift,4)}")
        if paid_bonus > 0:
            reasons.append(f"paid_bonus_applied: {round(paid_bonus,4)}")

        # spend-quality guardrail: if candidate paid but final score is low,
        # flag a low-fit warning so downstream systems can reconcile spend.
        low_fit_warning = False
        try:
            if candidate_id and job_id and is_paid(candidate_id, job_id) and final_score < LOW_FIT_THRESHOLD:
                low_fit_warning = True
                reasons.append(f"low_fit_warning: final_score={round(final_score,2)} < {LOW_FIT_THRESHOLD}")
        except Exception:
            low_fit_warning = False

    return {
        "final_score": round(final_score, 2),
        "recommendation": recommendation,
        "matched_skills": rule_result.get("matched_skills", []),
        "missing_skills": rule_result.get("missing_skills", []),
        "semantic_score": semantic_score,
        "reasons": reasons,
        "low_fit_warning": low_fit_warning
    }


def rank_jobs_for_student(resume_text, jobs, top_k=None, weights=(0.7, 0.3), protect_conversion=False, conversion_boost=0.1):
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

        res = score_resume_against_jd(resume_text, jd_text, weights=weights, protect_conversion=protect_conversion, conversion_boost=conversion_boost)
        res["job_id"] = job_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored


def rank_candidates_for_job(jd_text, candidates, top_k=None, weights=(0.7, 0.3), protect_conversion=False, conversion_boost=0.1, job_id=None):
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

        res = score_resume_against_jd(resume_text, jd_text, weights=weights, protect_conversion=protect_conversion, conversion_boost=conversion_boost, candidate_id=candidate_id, job_id=job_id)
        res["candidate_id"] = candidate_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored