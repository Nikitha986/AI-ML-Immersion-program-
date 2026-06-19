import pandas as pd

students = pd.read_csv("data/students.csv")
jobs = pd.read_csv("data/jobs.csv")


def calculate_match(student_id, job_id):

    student_df = students[students["student_id"] == student_id]
    job_df = jobs[jobs["job_id"] == job_id]

    if student_df.empty:
        raise ValueError(f"Student {student_id} not found")

    if job_df.empty:
        raise ValueError(f"Job {job_id} not found")

    student = student_df.iloc[0]
    job = job_df.iloc[0]

    reasons = []

    # Skill checks
    if student["python"] >= job["python_req"]:
        reasons.append("Python requirement satisfied")
    else:
        reasons.append("Python below requirement")

    if student["sql"] >= job["sql_req"]:
        reasons.append("SQL requirement satisfied")
    else:
        reasons.append("SQL below requirement")

    if student["machine_learning"] >= job["ml_req"]:
        reasons.append("Machine Learning requirement satisfied")
    else:
        reasons.append("Machine Learning below requirement")

    if student["cgpa"] >= job["min_cgpa"]:
        reasons.append("CGPA requirement satisfied")
    else:
        reasons.append("CGPA below requirement")

    # Skill score
    python_score = min(student["python"] / job["python_req"], 1)
    sql_score = min(student["sql"] / job["sql_req"], 1)
    ml_score = min(student["machine_learning"] / job["ml_req"], 1)

    skill_score = (
        python_score +
        sql_score +
        ml_score
    ) / 3 * 100

    # CGPA score
    cgpa_score = 100 if student["cgpa"] >= job["min_cgpa"] else 0

    # Experience score
    experience_score = min(student["experience_months"] / 6, 1) * 100

    # Project score
    project_score = min(student["projects"] / 5, 1) * 100

    # Final weighted score
    final_score = (
        0.7 * skill_score +
        0.1 * cgpa_score +
        0.1 * experience_score +
        0.1 * project_score
    )

    if final_score >= 85:
        recommendation = "Strong Match"
    elif final_score >= 65:
        recommendation = "Moderate Match"
    else:
        recommendation = "Weak Match"

    return {
        "student_id": student_id,
        "job_id": job_id,
        "student_name": student["name"],
        "job_title": job["title"],
        "match_score": round(final_score, 2),
        "recommendation": recommendation,
        "reasons": reasons
    }


def rank_candidates(job_id):

    results = []

    for student_id in students["student_id"]:

        result = calculate_match(student_id, job_id)

        results.append({
            "student_id": result["student_id"],
            "student_name": result["student_name"],
            "match_score": result["match_score"],
            "recommendation": result["recommendation"]
        })

    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return results