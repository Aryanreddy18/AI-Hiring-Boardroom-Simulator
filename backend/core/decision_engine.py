from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from backend.agents.hr_agent import evaluate_hr_fit
from backend.agents.manager_agent import evaluate_managerial_fit
from backend.agents.tech_agent import evaluate_technical_fit
from backend.core.debate_engine import run_debate
from backend.core.features_extractor import extract_candidate_features, extract_job_features
from backend.core.similarity import cosine_similarity_tokens, score_experience_match, score_skill_match


@dataclass
class HiringDecisionEngine:
    strong_hire_cutoff: float = 82.0
    hire_cutoff: float = 68.0

    def evaluate(self, resume_text: str, jd_text: str) -> Dict[str, object]:
        candidate_pack = extract_candidate_features(resume_text)
        job_pack = extract_job_features(jd_text)

        candidate_doc = candidate_pack["document"]
        job_doc = job_pack["document"]
        candidate_features = candidate_pack["features"]
        job_features = job_pack["features"]

        skill_match = score_skill_match(
            required_skills=job_features["required_skills"],
            preferred_skills=job_features["preferred_skills"],
            candidate_skills=candidate_features["skills"],
        )
        exp_match = score_experience_match(
            candidate_years=float(candidate_features["years_of_experience"]),
            min_required_years=float(job_features["min_years_of_experience"]),
        )
        text_similarity = cosine_similarity_tokens(
            candidate_doc["tokens"],
            job_doc["tokens"],
        )

        tech_review = evaluate_technical_fit(candidate_features, job_features, skill_match)
        manager_review = evaluate_managerial_fit(candidate_features, job_features, exp_match)
        hr_review = evaluate_hr_fit(candidate_features, job_features)

        reviews: List[Dict[str, object]] = [tech_review, manager_review, hr_review]
        debate = run_debate(reviews)

        final_score = (debate["weighted_score"] * 0.85) + (text_similarity * 100 * 0.15)
        final_score = round(final_score, 2)

        if final_score >= self.strong_hire_cutoff:
            decision = "strong_hire"
        elif final_score >= self.hire_cutoff:
            decision = "hire"
        elif final_score >= 55:
            decision = "hold"
        else:
            decision = "reject"

        explanation = self._build_explanation(decision, final_score, skill_match, exp_match, debate)

        return {
            "pipeline": {
                "input": {
                    "resume_length": len(resume_text or ""),
                    "jd_length": len(jd_text or ""),
                },
                "preprocessing": {
                    "resume_tokens": candidate_doc["token_count"],
                    "jd_tokens": job_doc["token_count"],
                },
                "candidate_features": candidate_features,
                "job_features": job_features,
                "similarity": {
                    "skill_match": skill_match,
                    "experience_match": round(exp_match, 3),
                    "text_similarity": round(text_similarity, 3),
                },
            },
            "agent_reviews": reviews,
            "debate": debate,
            "final_decision": {
                "decision": decision,
                "score": final_score,
                "explanation": explanation,
            },
        }

    @staticmethod
    def _build_explanation(
        decision: str,
        score: float,
        skill_match: Dict[str, float],
        exp_match: float,
        debate: Dict[str, object],
    ) -> str:
        return (
            f"Decision={decision} at score {score}. "
            f"Required-skill match is {skill_match['required_score']:.2f}, "
            f"experience alignment is {exp_match:.2f}, "
            f"and panel weighted score is {debate['weighted_score']:.2f}."
        )
