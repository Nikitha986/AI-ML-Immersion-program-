from .skills import extract_skills, extract_structured_skills
from .ontology import build_ontology_payload

def parse_jd(text):
    skills = extract_skills(text)
    structured_skills = extract_structured_skills(text)
    ontology = build_ontology_payload(skills)

    return {
        "required_skills": skills,
        "structured_skills": structured_skills,
        "ontology": ontology,
    }