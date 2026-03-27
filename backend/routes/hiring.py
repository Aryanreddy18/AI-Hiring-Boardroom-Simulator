from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.decision_engine import HiringDecisionEngine
from backend.core.interview_engine import InterviewEngine


router = APIRouter(prefix="/api/hiring", tags=["hiring"])
engine = HiringDecisionEngine()
interview_engine = InterviewEngine()


class HiringEvaluateRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Candidate resume content")
    jd_text: str = Field(..., min_length=20, description="Job description content")


class HiringEvaluateResponse(BaseModel):
    pipeline: dict
    agent_reviews: list
    debate: dict
    supervisor_review: dict
    final_decision: dict


@router.post("/evaluate", response_model=HiringEvaluateResponse)
def evaluate_candidate(payload: HiringEvaluateRequest):
    return engine.evaluate(payload.resume_text, payload.jd_text)


class StartInterviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    jd_text: str = Field(..., min_length=20)
    candidate_name: str = Field(default="Candidate", min_length=1)
    max_rounds: int = Field(default=2, ge=1, le=3)


class InterviewAnswerItem(BaseModel):
    agent: str = Field(..., min_length=2)
    answer_text: str = Field(..., min_length=3)


class SubmitAnswersRequest(BaseModel):
    answers: List[InterviewAnswerItem]


@router.get("/interview/initiate")
def initiate_interview():
    return interview_engine.initiate()


@router.post("/interview/start")
def start_interview(payload: StartInterviewRequest):
    return interview_engine.start_interview(
        resume_text=payload.resume_text,
        jd_text=payload.jd_text,
        candidate_name=payload.candidate_name,
        max_rounds=payload.max_rounds,
    )


@router.post("/interview/{session_id}/respond")
def submit_interview_answers(session_id: str, payload: SubmitAnswersRequest):
    try:
        return interview_engine.submit_round_answers(
            session_id=session_id,
            answers=[answer.model_dump() for answer in payload.answers],
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/interview/{session_id}/status")
def get_interview_status(session_id: str):
    try:
        return interview_engine.get_session_status(session_id=session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
