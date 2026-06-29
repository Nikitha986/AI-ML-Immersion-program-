import re

SKILL_CATEGORIES = {
    "programming_languages": ["python", "java", "c++"],
    "machine_learning": ["machine learning", "deep learning", "tensorflow", "pytorch"],
    "web_frameworks": ["fastapi", "django", "flask", "react"],
    "databases": ["sql", "mongodb", "postgresql"],
    "devops": ["docker", "aws", "kubernetes"],
}

SKILLS_ORDER = [
    skill for group in SKILL_CATEGORIES.values() for skill in group
]

SKILL_TO_CATEGORY = {
    skill: category
    for category, skills in SKILL_CATEGORIES.items()
    for skill in skills
}

SKILL_PATTERN = re.compile(
    r"\b(" + r"|".join(re.escape(skill) for skill in SKILLS_ORDER) + r")\b",
    flags=re.IGNORECASE,
)


def extract_skills(text):
    text = text or ""
    found = []
    for match in SKILL_PATTERN.finditer(text):
        skill = match.group(1).lower()
        if skill not in found:
            found.append(skill)
    return found


def extract_structured_skills(text):
    skills = extract_skills(text)
    structured = {category: [] for category in SKILL_CATEGORIES}
    for skill in skills:
        category = SKILL_TO_CATEGORY.get(skill)
        if category:
            structured[category].append(skill)
    return {cat: skills for cat, skills in structured.items() if skills}
