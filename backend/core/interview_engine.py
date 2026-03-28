from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
from typing import Dict, List
from uuid import uuid4

from backend.agents.hr_agent import evaluate_hr_answer
from backend.agents.manager_agent import evaluate_manager_answer
from backend.agents.supervisor_agent import finalize_interview_decision, supervise_interview_round
from backend.agents.tech_agent import evaluate_technical_answer
from backend.core.debate_engine import run_debate
from backend.core.decision_engine import HiringDecisionEngine
from backend.core.features_extractor import extract_job_features
from backend.core.llm_question_generator import generate_questions_with_featherless


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class InterviewSession:
    session_id: str
    candidate_name: str
    resume_text: str
    jd_text: str
    created_at: str
    max_rounds: int
    baseline_result: Dict[str, object]
    job_features: Dict[str, object]
    question_bank: Dict[str, List[str]]
    current_round: int = 0
    transcript: List[Dict[str, object]] = field(default_factory=list)
    round_reviews: List[Dict[str, object]] = field(default_factory=list)
    is_finished: bool = False
    video_call: Dict[str, object] = field(default_factory=dict)
    question_source: str = "rule_based"


class InterviewEngine:
    def __init__(self) -> None:
        self.sessions: Dict[str, InterviewSession] = {}
        self.decision_engine = HiringDecisionEngine()
        self.session_ttl_seconds = max(300, int(os.getenv("INTERVIEW_SESSION_TTL_SECONDS", "21600")))
        self.max_sessions = max(20, int(os.getenv("INTERVIEW_MAX_SESSIONS", "500")))

    def initiate(self) -> Dict[str, object]:
        return {
            "message": "Interview setup ready. Please provide resume_file and jd_text to start.",
            "required_fields": ["resume_file", "jd_text"],
            "optional_fields": ["candidate_name", "max_rounds"],
        }

    def start_interview(
        self,
        resume_text: str,
        jd_text: str,
        candidate_name: str = "Candidate",
        max_rounds: int = 2,
    ) -> Dict[str, object]:
        self._prune_sessions()
        baseline_result = self.decision_engine.evaluate(resume_text, jd_text)
        job_pack = extract_job_features(jd_text)
        job_features = job_pack["features"]

        rounds = max(1, min(3, max_rounds))
        question_bank, question_source = generate_questions_with_featherless(
            resume_text=resume_text,
            jd_text=jd_text,
            job_features=job_features,
            rounds=rounds,
        )

        session_id = str(uuid4())
        room_id = f"boardroom-{session_id[:8]}"
        session = InterviewSession(
            session_id=session_id,
            candidate_name=candidate_name,
            resume_text=resume_text,
            jd_text=jd_text,
            created_at=_utc_now(),
            max_rounds=rounds,
            baseline_result=baseline_result,
            job_features=job_features,
            question_bank=question_bank,
            video_call={
                "status": "started",
                "room_id": room_id,
                "join_url": f"https://video.boardroom.local/rooms/{room_id}",
                "started_at": _utc_now(),
            },
            question_source=question_source,
        )
        self.sessions[session_id] = session

        return {
            "session_id": session_id,
            "candidate_name": candidate_name,
            "video_call": session.video_call,
            "message": "Video call started and interview initiated.",
            "question_source": question_source,
            "current_round": 1,
            "questions": self._get_round_questions(session, round_index=0),
            "baseline_screening": baseline_result["final_decision"],
        }

    def submit_round_answers(self, session_id: str, answers: List[Dict[str, str]]) -> Dict[str, object]:
        self._prune_sessions()
        session = self._get_session(session_id)
        if session.is_finished:
            return {
                "session_id": session_id,
                "status": "finished",
                "final_result": self._build_final_result(session),
            }

        expected_questions = self._get_round_questions(session, session.current_round)
        expected_agents = {q["agent"] for q in expected_questions}
        answer_map = {str(a.get("agent", "")).lower(): str(a.get("answer_text", "")).strip() for a in answers}

        missing = sorted(expected_agents - set(answer_map))
        if missing:
            return {
                "session_id": session_id,
                "status": "invalid_payload",
                "message": f"Missing answers for agents: {', '.join(missing)}",
                "expected_agents": sorted(expected_agents),
            }

        this_round_reviews: List[Dict[str, object]] = []
        for question in expected_questions:
            agent = question["agent"]
            answer_text = answer_map[agent]
            if agent == "tech":
                review = evaluate_technical_answer(answer_text, session.job_features)
            elif agent == "manager":
                review = evaluate_manager_answer(answer_text)
            else:
                review = evaluate_hr_answer(answer_text)

            event = {
                "round": session.current_round + 1,
                "agent": agent,
                "question": question["question"],
                "answer_text": answer_text,
                "review": review,
                "timestamp": _utc_now(),
            }
            session.transcript.append(event)
            this_round_reviews.append(review)

        supervisor_round = supervise_interview_round(this_round_reviews)
        session.round_reviews.append(
            {
                "round": session.current_round + 1,
                "agent_reviews": this_round_reviews,
                "supervisor": supervisor_round,
            }
        )

        session.current_round += 1
        should_finish = supervisor_round["should_end_interview"] or session.current_round >= session.max_rounds
        if should_finish:
            session.is_finished = True
            return {
                "session_id": session_id,
                "status": "finished",
                "round_review": session.round_reviews[-1],
                "final_result": self._build_final_result(session),
            }

        return {
            "session_id": session_id,
            "status": "in_progress",
            "round_review": session.round_reviews[-1],
            "next_round": session.current_round + 1,
            "questions": self._get_round_questions(session, session.current_round),
        }

    def get_session_status(self, session_id: str) -> Dict[str, object]:
        self._prune_sessions()
        session = self._get_session(session_id)
        if session.is_finished:
            return {
                "session_id": session_id,
                "status": "finished",
                "final_result": self._build_final_result(session),
            }
        return {
            "session_id": session_id,
            "status": "in_progress",
            "current_round": session.current_round + 1,
            "questions": self._get_round_questions(session, session.current_round),
        }

    def _build_final_result(self, session: InterviewSession) -> Dict[str, object]:
        agent_scores = {"tech": [], "manager": [], "hr": []}
        for turn in session.transcript:
            agent = turn["agent"]
            score = float(turn["review"]["score"])
            if agent in agent_scores:
                agent_scores[agent].append(score)

        summarized_reviews = []
        for agent, scores in agent_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0.0
            vote = "hire" if avg_score >= 68 else ("hold" if avg_score >= 50 else "reject")
            summarized_reviews.append(
                {
                    "agent": agent,
                    "score": round(avg_score, 2),
                    "vote": vote,
                    "confidence": 0.8,
                }
            )

        debate = run_debate(summarized_reviews)
        interview_weighted = float(debate.get("weighted_score", 0.0))
        baseline_score = float(session.baseline_result["final_decision"]["score"])
        supervisor_final = finalize_interview_decision(
            baseline_score=baseline_score,
            interview_weighted_score=interview_weighted,
            conflict_count=len(debate.get("conflicts", [])),
        )

        return {
            "session_id": session.session_id,
            "candidate_name": session.candidate_name,
            "question_source": session.question_source,
            "video_call": session.video_call,
            "baseline_result": session.baseline_result["final_decision"],
            "interview_summary": {
                "rounds_completed": session.current_round,
                "agent_scores": {k: [round(v, 2) for v in vals] for k, vals in agent_scores.items()},
                "debate": debate,
            },
            "supervisor_final": supervisor_final,
            "final_decision": {
                "decision": supervisor_final["decision"],
                "score": supervisor_final["final_score"],
                "explanation": (
                    "Supervisor combined baseline screening and live interview scores "
                    "from Tech, Manager, and HR agents to produce the final hiring outcome."
                ),
            },
            "transcript": session.transcript,
        }

    def _get_round_questions(self, session: InterviewSession, round_index: int) -> List[Dict[str, object]]:
        agents = ("tech", "manager", "hr")
        questions: List[Dict[str, object]] = []
        for agent in agents:
            question_list = session.question_bank.get(agent, [])
            if round_index < len(question_list):
                questions.append(
                    {
                        "agent": agent,
                        "question_id": f"{agent}-r{round_index + 1}",
                        "question": question_list[round_index],
                    }
                )
        return questions

    def _get_session(self, session_id: str) -> InterviewSession:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Interview session '{session_id}' not found.")
        return session

    def _prune_sessions(self) -> None:
        now = datetime.now(timezone.utc)

        # Drop expired sessions first.
        expired_ids: List[str] = []
        for session_id, session in self.sessions.items():
            try:
                created = datetime.fromisoformat(session.created_at)
            except ValueError:
                created = now
            age = (now - created).total_seconds()
            if age > self.session_ttl_seconds:
                expired_ids.append(session_id)

        for session_id in expired_ids:
            self.sessions.pop(session_id, None)

        # Enforce max session cap by removing oldest sessions.
        if len(self.sessions) <= self.max_sessions:
            return

        ordered = sorted(
            self.sessions.values(),
            key=lambda s: s.created_at,
        )
        overflow = len(self.sessions) - self.max_sessions
        for session in ordered[:overflow]:
            self.sessions.pop(session.session_id, None)
