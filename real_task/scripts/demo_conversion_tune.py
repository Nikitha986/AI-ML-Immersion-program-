"""Demo: show ranking before and after conversion-tuning.

Run from repository root with PYTHONPATH set so package imports resolve.
Example:
    $env:PYTHONPATH='.'; python scripts/demo_conversion_tune.py
"""
import csv
from matching.ranking import rank_jobs_for_student


def load_jobs(path="data/jobs.csv"):
    jobs = []
    with open(path, newline='', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        for row in r:
            jobs.append({
                "job_id": row["job_id"],
                "jd_text": row["description"]
            })
    return jobs


def load_students(path="data/students.csv"):
    students = []
    with open(path, newline='', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        for row in r:
            students.append({
                "student_id": row["student_id"],
                "resume_text": row["resume_text"]
            })
    return students


def print_top(title, ranked, top=3):
    print(title)
    for i, r in enumerate(ranked[:top], 1):
        print(f"{i}. {r.get('job_id')} score={r.get('final_score')} reasons={r.get('reasons')}")
    print()


def main():
    jobs = load_jobs()
    students = load_students()

    # demo for first student
    s = students[0]
    resume = s["resume_text"]

    before = rank_jobs_for_student(resume, jobs, weights=(0.7, 0.3), top_k=3)
    after = rank_jobs_for_student(resume, jobs, weights=(0.7, 0.3), protect_conversion=True, conversion_boost=0.12, top_k=3)

    print_top("Top jobs before conversion tuning:", before)
    print_top("Top jobs after conversion tuning:", after)


if __name__ == "__main__":
    main()
