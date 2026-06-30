from parsing.resume_parser import parse_resume
from parsing.jd_parser import parse_jd
from matching.rule_matcher import rule_match
from matching.semantic_matcher import semantic_match
from payments.stub import is_paid

# threshold for low-fit warning (percent)
LOW_FIT_THRESHOLD = 60
# hardening signals for false-positive reduction
HARDENING_MIN_SEMANTIC = 55
HARDENING_MIN_MATCHED_FRAC = 0.25
HARDENING_MAX_PENALTY = 0.20


def _build_trust_signoff(final_score, semantic_score, matched_count, matched_frac, false_positive_warning, low_fit_warning):
    notes = []
    if matched_count == 0:
        notes.append("no_skill_overlap")
    if matched_frac < 0.3:
        notes.append("low_skill_coverage")
    if false_positive_warning:
        notes.append("hardening_penalty_applied")
    if low_fit_warning:
        notes.append("low_fit_warning")
    if semantic_score < 60:
        notes.append("semantic_score_below_target")

    status = "signed_off"
    if final_score < 75 or semantic_score < 60 or matched_count == 0 or false_positive_warning or low_fit_warning:
        status = "needs_review"

    if final_score >= 85 and semantic_score >= 75 and matched_count > 0 and not false_positive_warning:
        confidence = "high"
    elif final_score >= 65 and semantic_score >= 60:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "status": status,
        "confidence": confidence,
        "notes": notes,
    }


def _build_admin_flags(final_score, matched_count, false_positive_warning, low_fit_warning, recommendation):
    review_reasons = []
    if recommendation == "Weak Match":
        review_reasons.append("weak_match_score")
    if false_positive_warning:
        review_reasons.append("hardening_penalty")
    if low_fit_warning:
        review_reasons.append("low_fit_warning")
    if matched_count == 0:
        review_reasons.append("no_skill_overlap")

    weak_item_flag = bool(review_reasons) or final_score < 60
    return {
        "weak_item_flag": weak_item_flag,
        "needs_review": weak_item_flag,
        "review_reason": review_reasons,
    }


def rank_candidate(resume_text, jd_text):
    """Backward-compatible wrapper that scores a single resume vs a JD.

    Returns the same payload shape as before but delegates to the
    internal scoring helper so explainability fields are available.
    """
    return score_resume_against_jd(resume_text, jd_text)


def score_resume_against_jd(
    resume_text,
    jd_text,
    weights=(0.7, 0.3),
    protect_conversion=False,
    conversion_boost=0.1,
    protect_hardening=False,
    hardening_boost=0.1,
    candidate_id=None,
    job_id=None
):
    """Score a resume against a job description and return explainable payload.

    weights: tuple(rule_weight, semantic_weight)
    protect_conversion: when True, apply a small boost that favors candidates
        with higher semantic alignment and more matched skills (aimed to
        protect paid-apply conversion). `conversion_boost` is the maximum
        relative uplift applied to the final score (e.g. 0.1 => up to +10%).
    protect_hardening: when True, apply conservative hardening penalties to
        reduce false positives from low-confidence matches.
    """
    resume = parse_resume(resume_text)
    jd = parse_jd(jd_text)
    required_skills = jd.get("required_skills", [])

    rule_result = rule_match(
        resume.get("skills", []),
        required_skills
    )

    semantic_score = semantic_match(resume_text, jd_text)

    rule_w, sem_w = weights
    final_score = (rule_result["match_score"] * rule_w + semantic_score * sem_w)

    matched_count = len(rule_result.get("matched_skills", []))
    matched_frac = (matched_count / len(required_skills)) if required_skills else 0.0

    reasons = []
    if rule_result.get("matched_skills"):
        reasons.append("matched_skills: " + ", ".join(rule_result["matched_skills"]))
    if rule_result.get("missing_skills"):
        reasons.append("missing_skills: " + ", ".join(rule_result["missing_skills"]))
    reasons.append(f"semantic_score: {semantic_score}")

    false_positive_warning = False

    # Hardening guardrail: penalize low-confidence matches to reduce false positives.
    if protect_hardening:
        penalty = 0.0

        if matched_count == 0 and semantic_score < 50:
            penalty = min(HARDENING_MAX_PENALTY, hardening_boost + 0.1)
        elif matched_frac < HARDENING_MIN_MATCHED_FRAC and semantic_score < HARDENING_MIN_SEMANTIC:
            gap = HARDENING_MIN_MATCHED_FRAC - matched_frac
            semantic_gap = max(0.0, HARDENING_MIN_SEMANTIC - semantic_score) / 100.0
            penalty = min(HARDENING_MAX_PENALTY, hardening_boost * 0.5 + gap * 0.5 + semantic_gap * 0.25)
        elif semantic_score < 35:
            penalty = min(HARDENING_MAX_PENALTY, hardening_boost * 0.5)

        if penalty > 0.0:
            final_score = final_score * (1.0 - penalty)
            false_positive_warning = True
            reasons.append(
                f"hardening_applied: penalty={round(penalty,4)} matched_frac={round(matched_frac,3)} semantic_score={semantic_score}"
            )

    # Conversion protection tuning: favor candidates more likely to convert
    # by boosting final_score based on semantic alignment and matched skills.
    low_fit_warning = False
    if protect_conversion:
        signal = (semantic_score / 100.0) * matched_frac
        signal = max(0.0, min(1.0, signal))

        uplift = conversion_boost * signal
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

        try:
            if candidate_id and job_id and is_paid(candidate_id, job_id) and final_score < LOW_FIT_THRESHOLD:
                low_fit_warning = True
                reasons.append(
                    f"low_fit_warning: final_score={round(final_score,2)} < {LOW_FIT_THRESHOLD}"
                )
        except Exception:
            low_fit_warning = False

    recommendation = "Strong Match"
    if final_score < 80:
        recommendation = "Moderate Match"
    if final_score < 60:
        recommendation = "Weak Match"

    trust_signoff = _build_trust_signoff(
        final_score,
        semantic_score,
        matched_count,
        matched_frac,
        false_positive_warning,
        low_fit_warning,
    )
    admin_flags = _build_admin_flags(
        final_score,
        matched_count,
        false_positive_warning,
        low_fit_warning,
        recommendation,
    )
    explanation = (
        f"Matched {matched_count} of {len(required_skills)} required skills "
        f"with semantic similarity {semantic_score}."
    )
    if false_positive_warning:
        explanation += " The system applied a hardening penalty to reduce false positives."
    if low_fit_warning:
        explanation += " The recommendation is flagged for low-fit review."

    return {
        "final_score": round(final_score, 2),
        "recommendation": recommendation,
        "matched_skills": rule_result.get("matched_skills", []),
        "missing_skills": rule_result.get("missing_skills", []),
        "semantic_score": semantic_score,
        "reasons": reasons,
        "explanation": explanation,
        "low_fit_warning": low_fit_warning,
        "false_positive_warning": false_positive_warning,
        "trust_signoff": trust_signoff,
        "admin_flags": admin_flags,
        "ontology": {
            "resume": resume.get("ontology", {}),
            "job": jd.get("ontology", {}),
        },
    }


def rank_jobs_for_student(
    resume_text,
    jobs,
    top_k=None,
    weights=(0.7, 0.3),
    protect_conversion=False,
    conversion_boost=0.1,
    protect_hardening=False,
    hardening_boost=0.1
):
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

        res = score_resume_against_jd(
            resume_text,
            jd_text,
            weights=weights,
            protect_conversion=protect_conversion,
            conversion_boost=conversion_boost,
            protect_hardening=protect_hardening,
            hardening_boost=hardening_boost,
        )
        res["job_id"] = job_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored


def rank_candidates_for_job(
    jd_text,
    candidates,
    top_k=None,
    weights=(0.7, 0.3),
    protect_conversion=False,
    conversion_boost=0.1,
    protect_hardening=False,
    hardening_boost=0.1,
    job_id=None
):
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

        res = score_resume_against_jd(
            resume_text,
            jd_text,
            weights=weights,
            protect_conversion=protect_conversion,
            conversion_boost=conversion_boost,
            protect_hardening=protect_hardening,
            hardening_boost=hardening_boost,
            candidate_id=candidate_id,
            job_id=job_id
        )
        res["candidate_id"] = candidate_id
        scored.append(res)

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k] if top_k else scored