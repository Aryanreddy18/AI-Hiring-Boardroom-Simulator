from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from backend.core.decision_engine import HiringDecisionEngine


router = APIRouter(prefix="/api/hiring", tags=["hiring"])
engine = HiringDecisionEngine()


class HiringEvaluateRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Candidate resume content")
    jd_text: str = Field(..., min_length=20, description="Job description content")


class HiringEvaluateResponse(BaseModel):
    pipeline: dict
    agent_reviews: list
    debate: dict
    final_decision: dict


@router.post("/evaluate", response_model=HiringEvaluateResponse)
def evaluate_candidate(payload: HiringEvaluateRequest):
    return engine.evaluate(payload.resume_text, payload.jd_text)
