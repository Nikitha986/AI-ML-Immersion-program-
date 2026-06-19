from .skills import extract_skills

def parse_resume(text):

    skills = extract_skills(text)

    return {
        "skills": skills
    }