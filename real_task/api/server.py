from fastapi import FastAPI
from pydantic import BaseModel

from matching.ranking import (
    rank_candidate,
    rank_jobs_for_student,
    rank_candidates_for_job,
)
from baseline.matching import calculate_match
from payments.stub import mark_paid, is_paid

app = FastAPI()


class TextMatchRequest(BaseModel):
    resume_text: str
    jd_text: str


class JobRankRequest(BaseModel):
    job_id: str


class StudentRankRequest(BaseModel):
    resume_text: str


class JobCandidatesRequest(BaseModel):
    jd_text: str


class PayRequest(BaseModel):
    candidate_id: str
    job_id: str


class PayStatusRequest(BaseModel):
    candidate_id: str
    job_id: str


class JobRankConversionRequest(BaseModel):
    job_id: str
    protect_conversion: bool = False
    conversion_boost: float = 0.1


@app.post("/match_text")
def match_text(req: TextMatchRequest):
    result = rank_candidate(req.resume_text, req.jd_text)
    return result


@app.post("/rank_job")
def rank_job(req: JobRankRequest):
    # Return ranked candidates for a job id by loading data internally
    # Use baseline data loader via calculate_match helper as a fallback
    # Here we attempt to find job description from data and then rank
    from baseline.matching import _load_data

    students, jobs = _load_data()
    jrow = jobs[jobs["job_id"] == req.job_id]
    if jrow.empty:
        return {"candidates": []}

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    # build candidates list from students
    candidates = []
    for _, s in students.iterrows():
        candidates.append({"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")})

    results = rank_candidates_for_job(jd_text, candidates, job_id=req.job_id)
    return {"candidates": results}


@app.post("/pay")
def pay(req: PayRequest):
    mark_paid(req.candidate_id, req.job_id)
    return {"status": "ok", "candidate_id": req.candidate_id, "job_id": req.job_id}


@app.post("/is_paid")
def check_paid(req: PayStatusRequest):
    return {"candidate_id": req.candidate_id, "job_id": req.job_id, "is_paid": is_paid(req.candidate_id, req.job_id)}


@app.post("/rank_job_with_conversion")
def rank_job_with_conversion(req: JobRankConversionRequest):
    from baseline.matching import _load_data

    students, jobs = _load_data()
    jrow = jobs[jobs["job_id"] == req.job_id]
    if jrow.empty:
        return {"candidates": []}

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    candidates = []
    for _, s in students.iterrows():
        candidates.append({"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")})

    results = rank_candidates_for_job(jd_text, candidates, protect_conversion=req.protect_conversion, conversion_boost=req.conversion_boost, job_id=req.job_id)
    return {"candidates": results}


@app.post("/rank_jobs_for_student")
def rank_jobs(req: StudentRankRequest):
    # load jobs from baseline data and run ranking
    from baseline.matching import _load_data

    students, jobs = _load_data()
    jobs_list = []
    for _, j in jobs.iterrows():
        jobs_list.append({"job_id": j["job_id"], "jd_text": j.get("jd_text", j.get("description", ""))})

    ranked = rank_jobs_for_student(req.resume_text, jobs_list)
    return {"jobs": ranked}
