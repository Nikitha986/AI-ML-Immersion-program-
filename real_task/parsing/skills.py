KNOWN_SKILLS = {
    "python",
    "sql",
    "java",
    "c++",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "fastapi",
    "django",
    "flask",
    "docker",
    "aws",
    "kubernetes",
    "react",
    "mongodb",
    "postgresql"
}

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in KNOWN_SKILLS:
        if skill in text:
            found.append(skill)

    return list(set(found))