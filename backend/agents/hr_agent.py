from __future__ import annotations

from typing import Dict, List


def generate_hr_questions(rounds: int = 2) -> List[str]:
    questions: List[str] = [
        "Tell me about a conflict with a teammate and how you resolved it professionally.",
        "Why do you want this role, and what kind of team culture helps you perform best?",
        "Describe a time you received tough feedback and what changed afterward.",
    ]
    return questions[: max(1, rounds)]


def evaluate_hr_answer(answer_text: str) -> Dict[str, object]:
    normalized = (answer_text or "").lower()
    behavior_signal = 1.0 if any(t in normalized for t in ("team", "listen", "conflict", "collabor", "feedback")) else 0.65
    communication_signal = 1.0 if len(normalized.split()) >= 30 else 0.7
    growth_signal = 1.0 if any(t in normalized for t in ("learn", "improve", "adapt", "changed")) else 0.65

    score = ((behavior_signal * 0.4) + (communication_signal * 0.35) + (growth_signal * 0.25)) * 100
    score = round(min(100.0, score), 2)

    return {
        "agent": "hr",
        "score": score,
        "feedback": "Communication style, collaboration, and growth mindset were evaluated.",
    }


def evaluate_hr_fit(candidate_features: Dict[str, object], job_features: Dict[str, object]) -> Dict[str, object]:
    candidate_skill_count = len(candidate_features.get("skills", []))
    jd_skill_count = max(1, len(job_features.get("required_skills", [])) + len(job_features.get("preferred_skills", [])))

    alignment = min(1.0, candidate_skill_count / jd_skill_count)
    communication_signal = 1.0 if candidate_features.get("token_count", 0) > 120 else 0.75

    score = ((alignment * 0.6) + (communication_signal * 0.4)) * 100

    strengths: List[str] = []
    concerns: List[str] = []

    if communication_signal >= 1.0:
        strengths.append("Resume shows detailed and structured communication.")
    else:
        concerns.append("Resume is short; limited signal for role narrative.")

    vote = "hire" if score >= 65 else "hold"

    return {
        "agent": "hr",
        "score": round(score, 2),
        "vote": vote,
        "confidence": 0.77,
        "strengths": strengths,
        "concerns": concerns,
        "rationale": "HR assessed broad alignment, communication quality, and consistency.",
    }
