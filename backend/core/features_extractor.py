from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

from backend.utils.parser import extract_skills, normalize_text, preprocess_document, split_sentences


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


def _extract_jd_skill_buckets(raw_jd_text: str, all_skills: List[str]) -> tuple[List[str], List[str]]:
    all_skill_set = set(all_skills)
    if not all_skill_set:
        return [], []

    required_markers = ("required", "must", "mandatory", "minimum", "need", "essential")
    preferred_markers = ("preferred", "nice to have", "good to have", "plus", "bonus", "optional")

    required: set[str] = set()
    preferred: set[str] = set()

    for sentence in split_sentences(raw_jd_text):
        sentence_norm = normalize_text(sentence)
        if not sentence_norm:
            continue
        sentence_skills = set(extract_skills(sentence_norm, all_skill_set))
        if not sentence_skills:
            continue

        if any(marker in sentence_norm for marker in required_markers):
            required.update(sentence_skills)
        if any(marker in sentence_norm for marker in preferred_markers):
            preferred.update(sentence_skills)

    # Fallback when JD structure does not explicitly label required/preferred.
    if not required:
        ordered = [skill for skill in all_skills if skill in all_skill_set]
        split_idx = max(1, int(len(ordered) * 0.6))
        required = set(ordered[:split_idx])

    if not preferred:
        preferred = all_skill_set - required

    preferred -= required
    required_ordered = [skill for skill in all_skills if skill in required]
    preferred_ordered = [skill for skill in all_skills if skill in preferred]
    return required_ordered, preferred_ordered


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
    required, preferred = _extract_jd_skill_buckets(doc["raw_text"], all_skills)

    features = JobFeatures(
        required_skills=required,
        preferred_skills=preferred,
        min_years_of_experience=float(doc["years_of_experience"]),
        token_count=int(doc["token_count"]),
        summary=_summary_from_tokens(doc["tokens"]),
    )
    return {"document": doc, "features": asdict(features)}
