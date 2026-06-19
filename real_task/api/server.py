from fastapi import FastAPI
from pydantic import BaseModel

from matching.ranking import rank_candidate
from baseline.matching import rank_candidates

app = FastAPI()


class TextMatchRequest(BaseModel):
    resume_text: str
    jd_text: str


class JobRankRequest(BaseModel):
    job_id: str


@app.post("/match_text")
def match_text(req: TextMatchRequest):
    result = rank_candidate(req.resume_text, req.jd_text)
    return result


@app.post("/rank_job")
def rank_job(req: JobRankRequest):
    results = rank_candidates(req.job_id)
    return {"candidates": results}
