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


class BulkPayItem(BaseModel):
    candidate_id: str
    job_id: str


class BulkPayRequest(BaseModel):
    items: list[BulkPayItem]


class GenerateMetricsRequest(BaseModel):
    job_id: str | None = None
    candidate_ids: list[str] | None = None
    conversion_boost: float = 0.12


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


@app.post("/admin/mark_paid_bulk")
def mark_paid_bulk(req: BulkPayRequest):
    successes = []
    for item in req.items:
        try:
            mark_paid(item.candidate_id, item.job_id)
            successes.append({"candidate_id": item.candidate_id, "job_id": item.job_id, "status": "marked"})
        except Exception as e:
            successes.append({"candidate_id": item.candidate_id, "job_id": item.job_id, "status": f"error: {e}"})
    return {"results": successes}


@app.post("/admin/generate_paid_metrics")
def generate_paid_metrics(req: GenerateMetricsRequest):
    # Load baseline data
    from baseline.matching import _load_data
    import csv

    students, jobs = _load_data()

    # default job: first job
    if req.job_id is None:
        req.job_id = jobs.iloc[0]["job_id"]

    jrow = jobs[jobs["job_id"] == req.job_id]
    if jrow.empty:
        return {"candidates": [], "metrics_file": None}

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    # build candidates list optionally filtered by candidate_ids
    candidates = []
    for _, s in students.iterrows():
        cid = s["student_id"]
        if req.candidate_ids and cid not in req.candidate_ids:
            continue
        candidates.append({"candidate_id": cid, "resume_text": s.get("resume_text", "")})

    before = rank_candidates_for_job(jd_text, candidates, protect_conversion=False, job_id=req.job_id)
    after = rank_candidates_for_job(jd_text, candidates, protect_conversion=True, conversion_boost=req.conversion_boost, job_id=req.job_id)

    out_path = "experiments/paid_uplift_admin.csv"
    with open(out_path, "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "job_id", "pos_before", "score_before", "pos_after", "score_after", "paid"])
        for cid in [c["candidate_id"] for c in candidates]:
            def find(lst, cid):
                for i, r in enumerate(lst, 1):
                    if r.get("candidate_id") == cid:
                        return i, r.get("final_score")
                return None, None

            pos_b, score_b = find(before, cid)
            pos_a, score_a = find(after, cid)
            paid_flag = is_paid(cid, req.job_id)
            w.writerow([cid, req.job_id, pos_b or "", score_b or "", pos_a or "", score_a or "", paid_flag])

    return {"metrics_file": out_path, "job_id": req.job_id, "candidates": len(candidates)}


@app.post("/admin/spend_guardrail")
def spend_guardrail(job_id: str | None = None):
    # Generate spend_quality csv and return summary
    from baseline.matching import _load_data
    from payments.stub import is_paid
    import csv

    students, jobs = _load_data()
    if job_id is None:
        job_id = jobs.iloc[0]["job_id"]

    jrow = jobs[jobs["job_id"] == job_id]
    if jrow.empty:
        return {"rows": 0, "file": None}

    jd_text = jrow.iloc[0].get("jd_text") or jrow.iloc[0].get("description") or ""

    candidates = []
    for _, s in students.iterrows():
        candidates.append({"candidate_id": s["student_id"], "resume_text": s.get("resume_text", "")})

    results = rank_candidates_for_job(jd_text, candidates, protect_conversion=True, conversion_boost=0.12, job_id=job_id)

    out_path = "experiments/spend_quality.csv"
    rows = 0
    with open(out_path, "w", newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "job_id", "final_score", "low_fit_warning", "paid"])
        for r in results:
            cid = r.get("candidate_id")
            paid = is_paid(cid, job_id)
            if paid:
                w.writerow([cid, job_id, r.get("final_score"), r.get("low_fit_warning", False), paid])
                rows += 1

    return {"rows": rows, "file": out_path}


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
