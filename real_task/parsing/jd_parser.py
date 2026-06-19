from .skills import extract_skills

def parse_jd(text):

    skills = extract_skills(text)

    return {
        "required_skills": skills
    }