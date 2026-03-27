from __future__ import annotations

from typing import Dict, List


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
