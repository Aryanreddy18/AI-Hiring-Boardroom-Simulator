from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.core.decision_engine import HiringDecisionEngine
from backend.core.interview_engine import InterviewEngine
from backend.utils.parser import extract_resume_text_from_file


router = APIRouter(prefix="/api/hiring", tags=["hiring"])
engine = HiringDecisionEngine()
interview_engine = InterviewEngine()


class HiringEvaluateResponse(BaseModel):
    pipeline: dict
    agent_reviews: list
    debate: dict
    supervisor_review: dict
    final_decision: dict


@router.post("/evaluate", response_model=HiringEvaluateResponse)
async def evaluate_candidate(
    resume_file: UploadFile = File(..., description="Candidate resume file (PDF, DOCX, DOC, TXT, MD, RTF)"),
    jd_text: str = Form(..., min_length=20, description="Job description content"),
):
    try:
        resume_bytes = await resume_file.read()
        resume_text = extract_resume_text_from_file(resume_file.filename, resume_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if len(resume_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Resume content is too short after extraction.")

    return engine.evaluate(resume_text, jd_text)


class InterviewAnswerItem(BaseModel):
    agent: str = Field(..., min_length=2)
    answer_text: str = Field(..., min_length=3)


class SubmitAnswersRequest(BaseModel):
    answers: List[InterviewAnswerItem]


@router.get("/interview/initiate")
def initiate_interview():
    return interview_engine.initiate()


@router.post("/interview/start")
async def start_interview(
    resume_file: UploadFile = File(..., description="Candidate resume file (PDF, DOCX, DOC, TXT, MD, RTF)"),
    jd_text: str = Form(..., min_length=20, description="Job description content"),
    candidate_name: str = Form(default="Candidate", min_length=1),
    max_rounds: int = Form(default=2, ge=1, le=3),
):
    try:
        resume_bytes = await resume_file.read()
        resume_text = extract_resume_text_from_file(resume_file.filename, resume_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if len(resume_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Resume content is too short after extraction.")

    return interview_engine.start_interview(
        resume_text=resume_text,
        jd_text=jd_text,
        candidate_name=candidate_name,
        max_rounds=max_rounds,
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
