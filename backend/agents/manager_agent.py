from __future__ import annotations

from typing import Dict, List


def generate_manager_questions(job_features: Dict[str, object], rounds: int = 2) -> List[str]:
    min_years = float(job_features.get("min_years_of_experience", 0.0))
    questions: List[str] = [
        f"This role expects about {min_years:.0f}+ years ownership. Describe a project where you led execution end-to-end.",
        "How do you prioritize scope when deadlines slip and dependencies are blocked?",
        "Give an example of stakeholder alignment during a high-pressure release.",
    ]
    return questions[: max(1, rounds)]


def evaluate_manager_answer(answer_text: str) -> Dict[str, object]:
    normalized = (answer_text or "").lower()
    planning_signal = 1.0 if any(t in normalized for t in ("plan", "priorit", "timeline", "trade-off", "risk")) else 0.65
    ownership_signal = 1.0 if any(t in normalized for t in ("led", "owned", "delivered", "coordinated", "stakeholder")) else 0.65
    clarity_signal = 1.0 if len(normalized.split()) >= 35 else 0.7

    score = ((planning_signal * 0.4) + (ownership_signal * 0.4) + (clarity_signal * 0.2)) * 100
    score = round(min(100.0, score), 2)

    return {
        "agent": "manager",
        "score": score,
        "feedback": "Managerial ownership, prioritization, and delivery judgment were evaluated.",
    }


def evaluate_managerial_fit(candidate_features: Dict[str, object], job_features: Dict[str, object], experience_score: float) -> Dict[str, object]:
    candidate_years = float(candidate_features.get("years_of_experience", 0.0))
    min_years = float(job_features.get("min_years_of_experience", 0.0))

    experience_gap = candidate_years - min_years
    score = (experience_score * 0.75 + 0.25) * 100

    strengths: List[str] = []
    concerns: List[str] = []

    if experience_gap >= 0:
        strengths.append(f"Experience meets requirement by {experience_gap:.1f} years.")
    else:
        concerns.append(f"Experience below requirement by {abs(experience_gap):.1f} years.")

    vote = "hire" if score >= 68 else "hold"

    return {
        "agent": "manager",
        "score": round(score, 2),
        "vote": vote,
        "confidence": 0.81,
        "strengths": strengths,
        "concerns": concerns,
        "rationale": "Hiring manager emphasized scope ownership and delivery readiness.",
    }
