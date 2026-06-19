from parsing.resume_parser import parse_resume
from parsing.jd_parser import parse_jd
from matching.rule_matcher import rule_match
from matching.semantic_matcher import semantic_match

def rank_candidate(resume_text, jd_text):

    resume = parse_resume(resume_text)
    jd = parse_jd(jd_text)

    rule_result = rule_match(
        resume["skills"],
        jd["required_skills"]
    )

    semantic_score = semantic_match(
        resume_text,
        jd_text
    )

    final_score = (
        rule_result["match_score"] * 0.7 +
        semantic_score * 0.3
    )

    recommendation = "Strong Match"

    if final_score < 80:
        recommendation = "Moderate Match"

    if final_score < 60:
        recommendation = "Weak Match"

    return {
        "final_score": round(final_score, 2),
        "recommendation": recommendation,
        "matched_skills": rule_result["matched_skills"],
        "missing_skills": rule_result["missing_skills"],
        "semantic_score": semantic_score
    }