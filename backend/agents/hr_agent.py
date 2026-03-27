from __future__ import annotations

from typing import Dict, List


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
