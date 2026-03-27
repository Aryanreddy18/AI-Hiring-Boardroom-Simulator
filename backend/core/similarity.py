from __future__ import annotations

from collections import Counter
from math import sqrt
from typing import Dict, Iterable, List, Set


def jaccard_similarity(a: Iterable[str], b: Iterable[str]) -> float:
    set_a: Set[str] = set(a)
    set_b: Set[str] = set(b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def overlap_ratio(required: Iterable[str], available: Iterable[str]) -> float:
    req = set(required)
    avl = set(available)
    if not req:
        return 1.0
    return len(req & avl) / len(req)


def cosine_similarity_tokens(tokens_a: List[str], tokens_b: List[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0

    a_count = Counter(tokens_a)
    b_count = Counter(tokens_b)

    shared = set(a_count) & set(b_count)
    numerator = sum(a_count[t] * b_count[t] for t in shared)
    norm_a = sqrt(sum(v * v for v in a_count.values()))
    norm_b = sqrt(sum(v * v for v in b_count.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def score_skill_match(required_skills: List[str], preferred_skills: List[str], candidate_skills: List[str]) -> Dict[str, float]:
    required_score = overlap_ratio(required_skills, candidate_skills)
    preferred_score = overlap_ratio(preferred_skills, candidate_skills)
    jaccard = jaccard_similarity(set(required_skills + preferred_skills), candidate_skills)

    blended = (required_score * 0.6) + (preferred_score * 0.25) + (jaccard * 0.15)
    return {
        "required_score": required_score,
        "preferred_score": preferred_score,
        "jaccard_score": jaccard,
        "overall_skill_score": blended,
    }


def score_experience_match(candidate_years: float, min_required_years: float) -> float:
    if min_required_years <= 0:
        return 1.0
    ratio = candidate_years / min_required_years if min_required_years else 1.0
    return max(0.0, min(1.2, ratio)) / 1.2
