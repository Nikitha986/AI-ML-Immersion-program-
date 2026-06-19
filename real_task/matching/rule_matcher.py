def rule_match(resume_skills, jd_skills):

    matched = set(resume_skills).intersection(set(jd_skills))

    missing = set(jd_skills) - matched

    score = 0

    if len(jd_skills) > 0:
        score = len(matched) / len(jd_skills) * 100

    return {
        "match_score": round(score, 2),
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }