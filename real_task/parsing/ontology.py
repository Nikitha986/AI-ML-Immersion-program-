"""Simple skill ontology for resume and JD parsing.

This module defines a lightweight skill ontology and mapping helpers that
are used by parsing components to represent parsed skills in a structured
knowledge graph-like format.
"""

SKILL_ONTOLOGY = {
    "programming_languages": {
        "name": "Programming Languages",
        "description": "Core programming languages used in software development.",
        "skills": ["python", "java", "c++"],
    },
    "machine_learning": {
        "name": "Machine Learning",
        "description": "Machine learning and AI tools and frameworks.",
        "skills": ["machine learning", "deep learning", "tensorflow", "pytorch"],
    },
    "web_frameworks": {
        "name": "Web Frameworks",
        "description": "Web and application development frameworks.",
        "skills": ["fastapi", "django", "flask", "react"],
    },
    "databases": {
        "name": "Databases",
        "description": "Relational and NoSQL database technologies.",
        "skills": ["sql", "mongodb", "postgresql"],
    },
    "devops": {
        "name": "DevOps",
        "description": "Infrastructure, deployment, and cloud operations.",
        "skills": ["docker", "aws", "kubernetes"],
    },
}

SKILL_TO_CONCEPT = {
    skill: {
        "skill": skill,
        "category": category,
        "category_name": definition["name"],
        "path": f"Skill Ontology/{definition['name']}/{skill}",
    }
    for category, definition in SKILL_ONTOLOGY.items()
    for skill in definition["skills"]
}


def map_skills_to_ontology(skills):
    """Map a list of parsed skill strings to ontology concept nodes."""
    nodes = []
    for skill in skills:
        node = SKILL_TO_CONCEPT.get(skill)
        if node:
            nodes.append(node)
    return nodes


def build_ontology_payload(skills):
    """Return a structured ontology payload for parsed skills."""
    return {
        "root": "Skill Ontology",
        "nodes": map_skills_to_ontology(skills),
    }
