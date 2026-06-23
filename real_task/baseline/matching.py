import pandas as pd
from pathlib import Path

from matching.ranking import score_resume_against_jd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _load_data():
    students_path = DATA_DIR / "students.csv"
    jobs_path = DATA_DIR / "jobs.csv"

    if not students_path.exists() or not jobs_path.exists():
        raise FileNotFoundError(
            "Expected students.csv and jobs.csv in the project's data/ directory."
        )

    students = pd.read_csv(students_path)
    jobs = pd.read_csv(jobs_path)

    return students, jobs


def calculate_match(student_id, job_id):
    """Compute match for a student and job by id using `matching.ranking` helpers.

    Returns a dict with `match_score`, `recommendation`, and `reasons`.
    """
    students, jobs = _load_data()

    srow = students[students["student_id"] == student_id]
    jrow = jobs[jobs["job_id"] == job_id]

    if srow.empty or jrow.empty:
        raise ValueError("student_id or job_id not found in data files")

    resume_text = srow.iloc[0].get("resume_text") or srow.iloc[0].get("profile_text") or ""
    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    res = score_resume_against_jd(resume_text, jd_text)

    return {
        "match_score": res["final_score"],
        "recommendation": res["recommendation"],
        "reasons": res.get("reasons", [])
    }
