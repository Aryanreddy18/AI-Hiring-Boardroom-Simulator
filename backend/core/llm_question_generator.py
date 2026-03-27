from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict, List, Tuple


def _default_question_bank(job_features: Dict[str, object], rounds: int) -> Dict[str, List[str]]:
    required_skills = list(job_features.get("required_skills", []))
    preferred_skills = list(job_features.get("preferred_skills", []))
    min_years = float(job_features.get("min_years_of_experience", 0.0))

    tech = [
        f"Walk through a project where you used {required_skills[0] if required_skills else 'core backend technologies'} in production.",
        f"How would you design and test APIs with {required_skills[1] if len(required_skills) > 1 else 'strong reliability'} at scale?",
        f"How have you used {preferred_skills[0] if preferred_skills else 'modern deployment practices'} to improve outcomes?",
    ]
    manager = [
        f"This role expects about {min_years:.0f}+ years ownership. Describe end-to-end delivery ownership.",
        "How do you prioritize scope and risks under deadline pressure?",
        "Explain a difficult stakeholder alignment problem and your resolution.",
    ]
    hr = [
        "Describe a conflict with a teammate and how you resolved it.",
        "Why do you want this role and what team culture suits you best?",
        "Describe tough feedback you received and what changed afterward.",
    ]

    return {
        "tech": tech[: max(1, rounds)],
        "manager": manager[: max(1, rounds)],
        "hr": hr[: max(1, rounds)],
    }


def generate_questions_with_featherless(
    resume_text: str,
    jd_text: str,
    job_features: Dict[str, object],
    rounds: int,
) -> Tuple[Dict[str, List[str]], str]:
    api_key = os.getenv("FEATHERLESS_API_KEY", "").strip()
    if not api_key:
        return _default_question_bank(job_features, rounds), "rule_based"

    base_url = "https://api.featherless.ai/v1"
    model = "meta-llama/Meta-Llama-3.1-8B-Instruct"

    prompt = (
        "You are creating interview questions for 3 agents: tech, manager, hr. "
        f"Generate exactly {rounds} questions for each agent. "
        "Questions must be role-specific, concise, and aligned to the JD and candidate resume. "
        "Respond ONLY as strict JSON with keys: tech, manager, hr; each value is a list of strings.\n\n"
        f"Job description:\n{jd_text}\n\nResume:\n{resume_text}"
    )

    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": "You generate high-quality interview questions as strict JSON."},
            {"role": "user", "content": prompt},
        ],
    }

    req = urllib.request.Request(
        url=f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return _default_question_bank(job_features, rounds), "rule_based_fallback"

    try:
        parsed = json.loads(raw)
        content = parsed["choices"][0]["message"]["content"]
        data = json.loads(content)
        question_bank = {
            "tech": [str(q).strip() for q in data.get("tech", []) if str(q).strip()][:rounds],
            "manager": [str(q).strip() for q in data.get("manager", []) if str(q).strip()][:rounds],
            "hr": [str(q).strip() for q in data.get("hr", []) if str(q).strip()][:rounds],
        }
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return _default_question_bank(job_features, rounds), "rule_based_fallback"

    if not question_bank["tech"] or not question_bank["manager"] or not question_bank["hr"]:
        return _default_question_bank(job_features, rounds), "rule_based_fallback"

    return question_bank, "featherless"
