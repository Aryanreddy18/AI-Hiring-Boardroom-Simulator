from __future__ import annotations

from typing import Dict, List


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
