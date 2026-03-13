"""
Salary estimation logic using the Claude API.

Two modes:
  - Job description  → estimate what the role pays
  - Candidate profile → estimate what the candidate currently earns
"""

import json
import anthropic
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-6"


# ── Output schema ──────────────────────────────────────────────────────────────

class SalaryBreakdown(BaseModel):
    low: int
    high: int


class SalaryEstimate(BaseModel):
    role_title: str
    location: str
    seniority_level: str
    currency: str
    base_salary: SalaryBreakdown
    annual_bonus: Optional[SalaryBreakdown] = None
    bonus_note: Optional[str] = None
    equity_note: Optional[str] = None
    total_compensation: SalaryBreakdown
    confidence_pct: int
    confidence_rationale: str
    key_factors: list[str]
    caveats: list[str]


# ── JSON schema for output_config ─────────────────────────────────────────────

_SALARY_SCHEMA = {
    "type": "object",
    "properties": {
        "role_title": {"type": "string"},
        "location": {"type": "string"},
        "seniority_level": {"type": "string"},
        "currency": {"type": "string"},
        "base_salary": {
            "type": "object",
            "properties": {
                "low": {"type": "integer"},
                "high": {"type": "integer"},
            },
            "required": ["low", "high"],
            "additionalProperties": False,
        },
        "annual_bonus": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "low": {"type": "integer"},
                        "high": {"type": "integer"},
                    },
                    "required": ["low", "high"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "bonus_note": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "equity_note": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "total_compensation": {
            "type": "object",
            "properties": {
                "low": {"type": "integer"},
                "high": {"type": "integer"},
            },
            "required": ["low", "high"],
            "additionalProperties": False,
        },
        "confidence_pct": {"type": "integer"},
        "confidence_rationale": {"type": "string"},
        "key_factors": {"type": "array", "items": {"type": "string"}},
        "caveats": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "role_title", "location", "seniority_level", "currency",
        "base_salary", "annual_bonus", "bonus_note", "equity_note",
        "total_compensation", "confidence_pct", "confidence_rationale",
        "key_factors", "caveats",
    ],
    "additionalProperties": False,
}


# ── Prompts ────────────────────────────────────────────────────────────────────

_JOB_DESCRIPTION_SYSTEM = """You are a compensation benchmarking expert with deep knowledge of salary \
data across industries, roles, and geographies. You draw on aggregated data from \
Glassdoor, LinkedIn Salary, Levels.fyi, Payscale, Radford, and industry surveys.

Analyse the job description and estimate the salary range for the role. Consider:
- Role type, responsibilities, and seniority signals in the description
- Required skills, years of experience, and qualifications
- Location and local market rates (adjust for cost of living)
- Industry vertical and company type (startup / scale-up / enterprise / FAANG-tier)
- Typical total comp structures for this sector (base / bonus / equity norms)

Set confidence_pct based on data availability:
- 85–95 %: Common roles (SWE, finance, sales, marketing) in major cities with abundant public data
- 65–84 %: Moderate data availability, niche-ish location, or ambiguous seniority
- 40–64 %: Highly specialised roles, smaller markets, or very limited comparable data

Return all salary figures in whole numbers (no cents). Use the local currency for the location."""

_CANDIDATE_PROFILE_SYSTEM = """You are a senior talent acquisition specialist and compensation \
benchmarking expert. You help recruiters estimate what a candidate is likely earning \
before extending an offer.

Analyse the employment history and estimate the candidate's current salary. Consider:
- Current / most recent role title and level
- Total years of experience and tenure at current company
- Company tier (FAANG / growth-stage / startup / enterprise / agency / public sector)
- Location and local market rates
- Career progression and trajectory
- Skills, specialisations, and industry niche

Set confidence_pct based on the quality of available information:
- 85–95 %: Clear title, well-known company, common role type, stated location
- 65–84 %: Some ambiguity in level, company comp norms unclear, or regional data gaps
- 40–64 %: Sparse history, unusual career path, or very niche specialisation

Return all salary figures in whole numbers (no cents). Use the local currency for the location."""


# ── Core function ──────────────────────────────────────────────────────────────

def _call_claude(system: str, user_message: str) -> SalaryEstimate:
    client = anthropic.Anthropic()

    with client.messages.stream(
        model=MODEL,
        max_tokens=8096,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user_message}],
        output_config={"format": {"type": "json_schema", "schema": _SALARY_SCHEMA}},
    ) as stream:
        response = stream.get_final_message()

    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    return SalaryEstimate(**data)


# ── Public API ─────────────────────────────────────────────────────────────────

def estimate_from_job_description(job_description: str, location: str = "") -> SalaryEstimate:
    location_line = f"Location: {location.strip()}\n\n" if location.strip() else ""
    user_msg = f"{location_line}Job Description:\n{job_description}"
    return _call_claude(_JOB_DESCRIPTION_SYSTEM, user_msg)


def estimate_from_candidate_profile(profile: str, location: str = "") -> SalaryEstimate:
    location_line = f"Location: {location.strip()}\n\n" if location.strip() else ""
    user_msg = f"{location_line}Candidate Profile:\n{profile}"
    return _call_claude(_CANDIDATE_PROFILE_SYSTEM, user_msg)
