from __future__ import annotations

from typing import Dict, List


def generate_technical_questions(job_features: Dict[str, object], rounds: int = 2) -> List[str]:
    required_skills = list(job_features.get("required_skills", []))
    preferred_skills = list(job_features.get("preferred_skills", []))

    questions: List[str] = []
    if required_skills:
        questions.append(
            f"Walk me through a production project where you used {required_skills[0]} and how you handled failures."
        )
    if len(required_skills) > 1:
        questions.append(
            f"How would you design and test an API layer using {required_skills[1]} under high traffic?"
        )
    if preferred_skills:
        questions.append(
            f"How have you used {preferred_skills[0]} to improve performance, reliability, or deployment quality?"
        )
    questions.append("Describe a debugging incident where root-cause analysis changed your implementation plan.")

    return questions[: max(1, rounds)]


def evaluate_technical_answer(answer_text: str, job_features: Dict[str, object]) -> Dict[str, object]:
    normalized = (answer_text or "").lower()
    required_skills = list(job_features.get("required_skills", []))

    mention_hits = sum(1 for skill in required_skills if skill in normalized)
    depth_signal = 1.0 if len(normalized.split()) >= 45 else 0.7
    architecture_signal = 1.0 if any(
        token in normalized for token in ("design", "latency", "scal", "test", "failure", "monitor", "deploy")
    ) else 0.65

    score = ((mention_hits / max(1, len(required_skills))) * 0.5 + depth_signal * 0.25 + architecture_signal * 0.25) * 100
    score = round(min(100.0, score), 2)

    return {
        "agent": "tech",
        "score": score,
        "feedback": "Technical clarity and implementation depth were evaluated.",
    }


def evaluate_technical_fit(candidate_features: Dict[str, object], job_features: Dict[str, object], skill_match: Dict[str, float]) -> Dict[str, object]:
    candidate_skills = set(candidate_features.get("skills", []))
    required = set(job_features.get("required_skills", []))

    missing_required = sorted(required - candidate_skills)
    matched_required = sorted(required & candidate_skills)

    score = (
        (skill_match["required_score"] * 0.7)
        + (skill_match["preferred_score"] * 0.2)
        + (skill_match["jaccard_score"] * 0.1)
    ) * 100

    concerns: List[str] = []
    if missing_required:
        concerns.append(f"Missing required skills: {', '.join(missing_required)}")

    vote = "hire" if score >= 70 and len(missing_required) <= 2 else "hold"

    return {
        "agent": "tech",
        "score": round(score, 2),
        "vote": vote,
        "confidence": 0.84 if not missing_required else 0.72,
        "strengths": [f"Matched required skills: {', '.join(matched_required)}"] if matched_required else [],
        "concerns": concerns,
        "rationale": "Technical panel focused on required skill alignment and breadth.",
    }
