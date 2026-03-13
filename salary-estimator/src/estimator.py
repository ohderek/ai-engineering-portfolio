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

_CONFIDENCE_RUBRIC = """
CONFIDENCE SCORING — mechanical points-based system. Apply each rule exactly once. Same input must always produce the same score.

Start at 50 points, then apply each applicable modifier:

ADD points (each applied at most once):
  +20  Role title is high-volume with abundant survey data: SWE/engineer, product manager, data analyst/scientist,
       HR/people ops, sales/account executive, finance/accounting, marketing, legal, operations, recruiter
  +15  Location is a Tier-1 comp data city: NYC, SF/Bay Area, Seattle, Boston, LA, Chicago, Austin, Toronto,
       Vancouver, London, Dublin, Amsterdam, Berlin, Paris, Stockholm, Zurich, Sydney, Singapore, Hong Kong, Tokyo
  +10  Seniority signal is unambiguous: explicit level code (L4, L5, IC3, VP), OR job title contains
       "Senior"/"Staff"/"Principal"/"Director"/"Manager" AND years of experience range is ≤3 years wide
  +8   Industry has transparent comp benchmarks published publicly: tech, finance/banking, consulting, law, pharma/biotech
  +7   Employer is identifiable AND tier is clear: named Fortune-500/enterprise, known tech company, or
       explicitly stated funding stage (Series A, B, C, public)

SUBTRACT points (each applied at most once):
  -15  Seniority is ambiguous: years range >3 yrs wide (e.g. "3–10 years"), OR title is generic with no level
       signal ("Specialist", "Associate", "Coordinator" with no qualifier)
  -10  Location is Tier-2 or regional: any city NOT in the Tier-1 list above but still named
       (e.g. Shannon, Cork, Manchester, Phoenix, Denver, Melbourne outside CBD, secondary Irish/UK cities)
  -10  Role is niche with few public comparables (fewer than ~500 job postings publicly visible for exact spec)
  -8   Industry has opaque comp norms: government, non-profit, NGO, early-stage pre-seed/seed startup, creative/media
  -8   Location is entirely missing from the input
  -5   Equity component exists but vesting/structure is unknown, OR startup stage is unstated

Rules:
- Apply +15 OR -10 for location, never both (Tier-1 = +15, named Tier-2 = -10, missing = -8)
- Apply +10 OR -15 for seniority, never both
- Cap final score at 95. Floor at 40.
- State arithmetic explicitly in confidence_rationale: "50 +20 +10 −10 = 70"
- Do NOT round to multiples of 5. Use the exact arithmetic result.

SALARY RANGE WIDTH — range must be calibrated to confidence:
  Score 85–95: range width ≤ 10% of midpoint  (e.g. midpoint €75k → range €71k–€79k)
  Score 65–84: range width ≤ 18% of midpoint  (e.g. midpoint €75k → range €68k–€82k)
  Score 40–64: range width ≤ 30% of midpoint  (e.g. midpoint €75k → range €64k–€86k)
A wide range paired with a high confidence score is a contradiction — avoid it."""


_JOB_DESCRIPTION_SYSTEM = f"""You are a compensation benchmarking expert with deep knowledge of salary \
data across industries, roles, and geographies. You draw on aggregated data from \
Glassdoor, LinkedIn Salary, Levels.fyi, Payscale, Radford, and industry surveys.

Analyse the job description and estimate the salary range for the role. Consider:
- Role type, responsibilities, and seniority signals in the description
- Required skills, years of experience, and qualifications
- Location and local market rates (adjust for cost of living)
- Industry vertical and company type (startup / scale-up / enterprise / FAANG-tier)
- Typical total comp structures for this sector (base / bonus / equity norms)

{_CONFIDENCE_RUBRIC}

Return all salary figures in whole numbers (no cents). Use the local currency for the location."""


_CANDIDATE_PROFILE_SYSTEM = f"""You are a senior talent acquisition specialist and compensation \
benchmarking expert. You help recruiters estimate what a candidate is likely earning \
before extending an offer.

Analyse the employment history and estimate the candidate's current salary. Consider:
- Current / most recent role title and level
- Total years of experience and tenure at current company
- Company tier (FAANG / growth-stage / startup / enterprise / agency / public sector)
- Location and local market rates
- Career progression and trajectory
- Skills, specialisations, and industry niche

{_CONFIDENCE_RUBRIC}

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
