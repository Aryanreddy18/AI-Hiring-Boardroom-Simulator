from __future__ import annotations

from typing import Dict, List


def supervise_panel(
    agent_reviews: List[Dict[str, object]],
    debate_summary: Dict[str, object],
    text_similarity: float,
    strong_hire_cutoff: float,
    hire_cutoff: float,
) -> Dict[str, object]:
    weighted_score = float(debate_summary.get("weighted_score", 0.0))
    conflict_count = len(debate_summary.get("conflicts", []))
    votes = debate_summary.get("votes", {"hire": 0, "hold": 0, "reject": 0})

    blended_score = (weighted_score * 0.85) + (text_similarity * 100 * 0.15)
    blended_score = round(blended_score, 2)

    if blended_score >= strong_hire_cutoff:
        decision = "strong_hire"
    elif blended_score >= hire_cutoff:
        decision = "hire"
    elif blended_score >= 55:
        decision = "hold"
    else:
        decision = "reject"

    override_reason = ""
    if conflict_count >= 2 and decision in {"strong_hire", "hire"}:
        decision = "hold"
        override_reason = "Supervisor downgraded decision to hold due to multi-point panel conflict."

    if votes.get("reject", 0) >= 2:
        decision = "reject"
        override_reason = "Supervisor enforced reject because majority reject votes were present."

    confidence = 0.88
    if conflict_count:
        confidence -= min(0.2, conflict_count * 0.08)
    confidence = round(max(0.5, confidence), 2)

    return {
        "agent": "supervisor",
        "blended_score": blended_score,
        "decision": decision,
        "confidence": confidence,
        "override_reason": override_reason,
        "rationale": (
            "Supervisor merged weighted panel score, vote distribution, "
            "conflict intensity, and text-level alignment into a final control decision."
        ),
        "snapshot": {
            "weighted_score": weighted_score,
            "text_similarity": round(text_similarity, 3),
            "votes": votes,
            "conflict_count": conflict_count,
            "agent_count": len(agent_reviews),
        },
    }


def supervise_interview_round(round_reviews: List[Dict[str, object]]) -> Dict[str, object]:
    if not round_reviews:
        return {
            "agent": "supervisor",
            "round_score": 0.0,
            "status": "insufficient_signal",
            "note": "No round reviews submitted.",
            "should_end_interview": False,
        }

    avg_score = sum(float(r.get("score", 0.0)) for r in round_reviews) / len(round_reviews)
    low_scores = [r for r in round_reviews if float(r.get("score", 0.0)) < 40]

    should_end = avg_score < 35 or len(low_scores) >= 2
    status = "critical" if should_end else ("watch" if avg_score < 60 else "healthy")
    note = "Supervisor is monitoring agent-specific quality signals for consistency."

    return {
        "agent": "supervisor",
        "round_score": round(avg_score, 2),
        "status": status,
        "note": note,
        "should_end_interview": should_end,
    }


def finalize_interview_decision(
    baseline_score: float,
    interview_weighted_score: float,
    conflict_count: int,
) -> Dict[str, object]:
    final_score = round((baseline_score * 0.6) + (interview_weighted_score * 0.4), 2)

    if final_score >= 82:
        decision = "strong_hire"
    elif final_score >= 68:
        decision = "hire"
    elif final_score >= 55:
        decision = "hold"
    else:
        decision = "reject"

    if conflict_count >= 2 and decision in {"strong_hire", "hire"}:
        decision = "hold"

    return {
        "agent": "supervisor",
        "final_score": final_score,
        "decision": decision,
        "baseline_score": round(baseline_score, 2),
        "interview_weighted_score": round(interview_weighted_score, 2),
        "conflict_count": conflict_count,
    }
