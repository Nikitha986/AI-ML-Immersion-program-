from .skills import extract_skills, extract_structured_skills

def parse_jd(text):
    skills = extract_skills(text)
    structured_skills = extract_structured_skills(text)

    return {
        "required_skills": skills,
        "structured_skills": structured_skills,
    }