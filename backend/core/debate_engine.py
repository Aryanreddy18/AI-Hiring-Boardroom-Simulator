from __future__ import annotations

from statistics import mean
from typing import Dict, List


AGENT_WEIGHTS = {
    "tech": 0.45,
    "manager": 0.35,
    "hr": 0.20,
}


def run_debate(agent_reviews: List[Dict[str, object]]) -> Dict[str, object]:
    if not agent_reviews:
        return {
            "weighted_score": 0.0,
            "raw_average_score": 0.0,
            "votes": {"hire": 0, "hold": 0, "reject": 0},
            "conflicts": ["No agent reviews available."],
            "resolution_notes": ["Insufficient data to debate."],
        }

    weighted_score = 0.0
    scores: List[float] = []
    votes = {"hire": 0, "hold": 0, "reject": 0}

    for review in agent_reviews:
        agent = str(review.get("agent", "")).lower()
        score = float(review.get("score", 0.0))
        vote = str(review.get("vote", "hold")).lower()

        scores.append(score)
        weighted_score += score * AGENT_WEIGHTS.get(agent, 0.0)
        if vote in votes:
            votes[vote] += 1
        else:
            votes["hold"] += 1

    spread = max(scores) - min(scores) if scores else 0.0
    conflicts: List[str] = []

    if spread >= 25:
        conflicts.append(f"High scoring disagreement detected (spread: {spread:.1f}).")
    if votes["hire"] and (votes["hold"] or votes["reject"]):
        conflicts.append("Vote mismatch across panel members.")

    resolution_notes = []
    if conflicts:
        resolution_notes.append("Applied weighted voting to prioritize technical and managerial fit.")
        resolution_notes.append("Final decision calibrated using both consensus and score spread.")
    else:
        resolution_notes.append("Panel reached stable alignment with low disagreement.")

    return {
        "weighted_score": round(weighted_score, 2),
        "raw_average_score": round(mean(scores), 2),
        "votes": votes,
        "conflicts": conflicts,
        "resolution_notes": resolution_notes,
    }
