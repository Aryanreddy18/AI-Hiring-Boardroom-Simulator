from __future__ import annotations

import re
from typing import Dict, List, Set

SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "nosql",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "fastapi",
    "flask",
    "django",
    "react",
    "node",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "git",
    "ci/cd",
    "microservices",
    "rest",
    "graphql",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
}

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+\-/.#]*")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_YOE_RE = re.compile(
    r"(?P<years>\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r", " ").replace("\n", " ").strip().lower()
    return re.sub(r"\s+", " ", cleaned)


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return _WORD_RE.findall(text.lower())


def extract_years_of_experience(text: str) -> float:
    if not text:
        return 0.0
    values: List[float] = []
    for match in _YOE_RE.finditer(text):
        try:
            values.append(float(match.group("years")))
        except (TypeError, ValueError):
            continue
    if not values:
        return 0.0
    # Highest value usually reflects total experience.
    return max(values)


def extract_skills(text: str, skill_lexicon: Set[str] | None = None) -> List[str]:
    lexicon = skill_lexicon or SKILL_KEYWORDS
    normalized = normalize_text(text)
    found: Set[str] = set()

    for skill in lexicon:
        if skill in normalized:
            found.add(skill)

    # Pick up simple "skills: x, y, z" patterns.
    skills_blocks = re.findall(r"skills?\s*[:\-]\s*([^.;]+)", normalized)
    for block in skills_blocks:
        for token in re.split(r"[,|/]", block):
            token = token.strip()
            if not token:
                continue
            if token in lexicon:
                found.add(token)
            elif len(token) > 2 and token.isascii():
                found.add(token)

    return sorted(found)


def preprocess_document(text: str) -> Dict[str, object]:
    normalized = normalize_text(text)
    sentences = split_sentences(text)
    tokens = tokenize(normalized)

    return {
        "raw_text": text or "",
        "normalized_text": normalized,
        "sentences": sentences,
        "tokens": tokens,
        "token_count": len(tokens),
        "skills": extract_skills(normalized),
        "years_of_experience": extract_years_of_experience(normalized),
    }
