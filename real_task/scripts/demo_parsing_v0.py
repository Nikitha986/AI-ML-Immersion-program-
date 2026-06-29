"""Demo script for parsing v0: extract structured skills from resumes and JDs.

Run from repository root with PYTHONPATH='.' if needed.
Example:
    python scripts/demo_parsing_v0.py
"""

import csv
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from parsing.resume_parser import parse_resume
from parsing.jd_parser import parse_jd


def load_students(path="data/students.csv"):
    students = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            students.append(row)
    return students


def load_jobs(path="data/jobs.csv"):
    jobs = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            jobs.append(row)
    return jobs


def main():
    students = load_students()
    jobs = load_jobs()

    print("=== Resume parsing v0 ===")
    for s in students:
        parsed = parse_resume(s.get("resume_text", ""))
        print(f"{s['student_id']} - {s['student_name']}")
        print("  skills:", parsed["skills"])
        print("  structured_skills:", parsed["structured_skills"])
        print("  ontology:", parsed["ontology"])
        print()

    print("=== JD parsing v0 ===")
    for j in jobs:
        parsed = parse_jd(j.get("description", ""))
        print(f"{j['job_id']} - {j['job_title']}")
        print("  required_skills:", parsed["required_skills"])
        print("  structured_skills:", parsed["structured_skills"])
        print("  ontology:", parsed["ontology"])
        print()


if __name__ == "__main__":
    main()
