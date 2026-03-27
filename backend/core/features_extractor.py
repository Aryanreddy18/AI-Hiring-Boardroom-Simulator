from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

from backend.utils.parser import preprocess_document


@dataclass
class CandidateFeatures:
    skills: List[str]
    years_of_experience: float
    token_count: int
    summary: str


@dataclass
class JobFeatures:
    required_skills: List[str]
    preferred_skills: List[str]
    min_years_of_experience: float
    token_count: int
    summary: str


def _summary_from_tokens(tokens: List[str], max_words: int = 40) -> str:
    if not tokens:
        return ""
    return " ".join(tokens[:max_words])


def extract_candidate_features(resume_text: str) -> Dict[str, object]:
    doc = preprocess_document(resume_text)
    features = CandidateFeatures(
        skills=doc["skills"],
        years_of_experience=float(doc["years_of_experience"]),
        token_count=int(doc["token_count"]),
        summary=_summary_from_tokens(doc["tokens"]),
    )
    return {"document": doc, "features": asdict(features)}


def extract_job_features(job_description_text: str) -> Dict[str, object]:
    doc = preprocess_document(job_description_text)
    all_skills = doc["skills"]
    required = all_skills[: max(1, int(len(all_skills) * 0.6))]
    preferred = all_skills[max(1, int(len(all_skills) * 0.6)) :]

    features = JobFeatures(
        required_skills=required,
        preferred_skills=preferred,
        min_years_of_experience=float(doc["years_of_experience"]),
        token_count=int(doc["token_count"]),
        summary=_summary_from_tokens(doc["tokens"]),
    )
    return {"document": doc, "features": asdict(features)}
