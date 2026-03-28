from __future__ import annotations

from io import BytesIO
import re
from typing import Dict, List, Set


SUPPORTED_RESUME_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".md",
    ".rtf",
}

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
    tokens = set(tokenize(normalized))
    found: Set[str] = set()

    for skill in lexicon:
        skill_norm = skill.strip().lower()
        if not skill_norm:
            continue

        # Use token and boundary-aware matching to avoid false positives
        # like "java" matching inside "javascript".
        if " " in skill_norm:
            pattern = rf"(?<![a-z0-9]){re.escape(skill_norm)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                found.add(skill_norm)
        elif skill_norm in tokens:
            found.add(skill_norm)
        else:
            pattern = rf"(?<![a-z0-9]){re.escape(skill_norm)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                found.add(skill_norm)

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


def extract_resume_text_from_file(filename: str | None, content: bytes) -> str:
    if not content:
        raise ValueError("Uploaded resume file is empty.")

    extension = ""
    if filename and "." in filename:
        extension = filename[filename.rfind(".") :].lower()

    if extension and extension not in SUPPORTED_RESUME_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_RESUME_EXTENSIONS))
        raise ValueError(f"Unsupported resume format '{extension}'. Supported formats: {supported}.")

    if extension == ".pdf":
        return _extract_pdf_text(content)
    if extension == ".docx":
        return _extract_docx_text(content)
    if extension == ".doc":
        return _extract_legacy_doc_text(content)
    return _decode_text_content(content)


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF parsing dependency is missing. Install 'pypdf'.") from exc

    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ValueError("Unable to read the PDF resume file.") from exc

    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in pages if page)
    return text.strip()


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ValueError("Word parsing dependency is missing. Install 'python-docx'.") from exc

    try:
        doc = Document(BytesIO(content))
    except Exception as exc:
        raise ValueError("Unable to read the DOCX resume file.") from exc

    lines = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    return "\n".join(lines).strip()


def _extract_legacy_doc_text(content: bytes) -> str:
    # Legacy .doc is a binary format. We perform a best-effort extraction
    # of printable segments, and ask for .docx/.pdf if no useful content exists.
    decoded = content.decode("latin-1", errors="ignore")
    words = re.findall(r"[A-Za-z][A-Za-z0-9@+.#/\-]{1,}", decoded)
    text = " ".join(words)
    if len(text) < 40:
        raise ValueError("Unable to extract text from .doc file. Please upload .docx or .pdf.")
    return text


def _decode_text_content(content: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return content.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode resume file content.")
