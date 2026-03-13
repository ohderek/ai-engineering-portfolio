"""
Salary Estimator — Streamlit UI
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CompIQ", page_icon="◈", layout="centered")

# ── Globals ────────────────────────────────────────────────────────────────────

CURRENCY_SYMBOLS = {
    "USD": "$", "GBP": "£", "EUR": "€",
    "CAD": "CA$", "AUD": "A$", "SGD": "S$",
}

def fmt(amount: int, currency: str = "USD") -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency + "\u00a0")
    return f"{symbol}{amount // 1000}k" if amount >= 1_000 else f"{symbol}{amount:,}"

def fmt_range(low: int, high: int, currency: str) -> str:
    return f"{fmt(low, currency)} – {fmt(high, currency)}"


# ── Page CSS ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Space+Mono:wght@400;700&display=swap');

/* ── Base ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif !important;
}
.stApp {
    background: #080b12 !important;
}
.block-container {
    max-width: 760px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 5rem !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Inputs ───────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea {
    background: #0f1420 !important;
    border: 1px solid #1e2535 !important;
    color: #d4d8e8 !important;
    border-radius: 6px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    caret-color: #e8c547 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #e8c547 !important;
    box-shadow: 0 0 0 3px rgba(232,197,71,0.08) !important;
    outline: none !important;
}
.stTextInput label,
.stTextArea label {
    color: #4a5270 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
::placeholder { color: #2a3048 !important; }

/* ── Button ───────────────────────────────────────── */
.stButton > button {
    background: #e8c547 !important;
    color: #080b12 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.6rem 1.4rem !important;
    transition: background 0.15s, transform 0.1s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    background: #f2d458 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(232,197,71,0.2) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Tabs ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e2535 !important;
    gap: 0 !important;
    margin-bottom: 1.75rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #3a4260 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.75rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    text-transform: uppercase !important;
    transition: color 0.15s !important;
}
.stTabs [aria-selected="true"] {
    color: #d4d8e8 !important;
    border-bottom: 2px solid #e8c547 !important;
}

/* ── Spinner ──────────────────────────────────────── */
.stSpinner p { color: #4a5270 !important; font-size: 0.8rem !important; }

/* ── Alerts ───────────────────────────────────────── */
.stAlert {
    background: #0f1420 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 6px !important;
    color: #d4d8e8 !important;
}

/* ── Body text ────────────────────────────────────── */
p, li { color: #4a5270 !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-bottom:2.5rem; padding-bottom:1.75rem; border-bottom:1px solid #1e2535">
  <div style="font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800;
              letter-spacing:-0.04em; color:#d4d8e8; line-height:1; margin-bottom:0.5rem">
    Comp<span style="color:#e8c547">IQ</span>
  </div>
  <div style="font-size:0.78rem; color:#3a4260; letter-spacing:0.08em; text-transform:uppercase;
              font-family:'Instrument Sans',sans-serif; font-weight:600">
    Compensation intelligence &nbsp;·&nbsp; Powered by Claude
  </div>
</div>
""", unsafe_allow_html=True)


# ── Results card ───────────────────────────────────────────────────────────────

def _conf_class(pct: int) -> str:
    if pct >= 80: return "high"
    if pct >= 60: return "med"
    return "low"

def _conf_label(pct: int) -> str:
    if pct >= 80: return "High confidence"
    if pct >= 60: return "Medium confidence"
    return "Low confidence"

def _conf_color(cls: str) -> str:
    return {"high": "#34d399", "med": "#fb923c", "low": "#f87171"}[cls]

def _conf_bg(cls: str) -> str:
    return {"high": "rgba(52,211,153,0.07)", "med": "rgba(251,146,60,0.07)", "low": "rgba(248,113,113,0.07)"}[cls]

def _conf_border(cls: str) -> str:
    return {"high": "rgba(52,211,153,0.25)", "med": "rgba(251,146,60,0.25)", "low": "rgba(248,113,113,0.25)"}[cls]

def _factors_html(items: list[str], icon: str, label: str) -> str:
    if not items:
        return ""
    lis = "".join(f'<li style="padding:0.25rem 0; color:#4a5270; border-bottom:1px solid #1a1f2e">{i}</li>' for i in items)
    return f"""
<details style="margin-top:0.75rem">
  <summary style="cursor:pointer; font-size:0.68rem; font-weight:600; letter-spacing:0.1em;
                  text-transform:uppercase; color:#2e3550; padding:0.6rem 0; list-style:none;
                  display:flex; align-items:center; gap:0.4rem; user-select:none">
    <span style="color:#2e3550">{icon}</span> {label}
  </summary>
  <ul style="margin:0.5rem 0 0; padding:0 0 0 0.25rem; list-style:none; font-size:0.82rem;
             font-family:'Instrument Sans',sans-serif">
    {lis}
  </ul>
</details>"""


def display_results(estimate) -> None:
    cc = _conf_class(estimate.confidence_pct)
    col = _conf_color(cc)
    bg  = _conf_bg(cc)
    bdr = _conf_border(cc)
    bar_pct = estimate.confidence_pct

    # Salary figures
    base  = fmt_range(estimate.base_salary.low, estimate.base_salary.high, estimate.currency)
    total = fmt_range(estimate.total_compensation.low, estimate.total_compensation.high, estimate.currency)

    if estimate.annual_bonus:
        bonus_val = fmt_range(estimate.annual_bonus.low, estimate.annual_bonus.high, estimate.currency)
        bonus_note_html = f'<div style="font-size:0.7rem;color:#2e3550;margin-top:0.3rem;font-style:italic">{estimate.bonus_note or ""}</div>'
    else:
        bonus_val = "—"
        bonus_note_html = f'<div style="font-size:0.7rem;color:#2e3550;margin-top:0.3rem;font-style:italic">{estimate.bonus_note or "Not typical"}</div>'

    equity_html = ""
    if estimate.equity_note:
        equity_html = f"""
<div style="background:#0c1018; border:1px solid #1e2535; border-radius:6px;
            padding:0.7rem 1rem; margin-bottom:1.25rem; display:flex; align-items:center; gap:0.75rem">
  <span style="font-size:0.65rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
               color:#2e3550; white-space:nowrap; font-family:'Instrument Sans',sans-serif">Equity</span>
  <span style="font-size:0.85rem; color:#6b7a9e; font-family:'Instrument Sans',sans-serif">{estimate.equity_note}</span>
</div>"""

    factors_html = _factors_html(estimate.key_factors, "◦", "Key factors")
    caveats_html  = _factors_html(estimate.caveats,     "⚠", "Caveats")

    st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">

<div style="background:#0c1018; border:1px solid #1e2535; border-radius:10px;
            padding:1.75rem; margin-top:1.5rem; font-family:'Instrument Sans',sans-serif">

  <!-- Header row -->
  <div style="display:flex; justify-content:space-between; align-items:flex-start;
              margin-bottom:1.5rem; padding-bottom:1.5rem; border-bottom:1px solid #1a1f2e">
    <div>
      <div style="font-family:'Syne',sans-serif; font-size:1.35rem; font-weight:800;
                  letter-spacing:-0.02em; color:#d4d8e8; line-height:1.2; margin-bottom:0.35rem">
        {estimate.role_title}
      </div>
      <div style="font-size:0.75rem; color:#3a4260; letter-spacing:0.04em">
        📍 {estimate.location} &nbsp;·&nbsp; {estimate.seniority_level}
      </div>
    </div>
    <div style="background:{bg}; border:1px solid {bdr}; border-radius:100px;
                padding:0.35rem 0.85rem; text-align:center; white-space:nowrap; flex-shrink:0">
      <div style="font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:{col};
                  line-height:1">{estimate.confidence_pct}%</div>
      <div style="font-size:0.6rem; color:{col}; opacity:0.75; letter-spacing:0.06em;
                  text-transform:uppercase; margin-top:0.15rem">{_conf_label(estimate.confidence_pct)}</div>
    </div>
  </div>

  <!-- Comp grid -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.75rem; margin-bottom:1.25rem">

    <div style="background:#080b12; border:1px solid #1a1f2e; border-radius:6px; padding:1rem">
      <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:#2e3550; margin-bottom:0.45rem">Base Salary</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700;
                  color:#c4c8d8; line-height:1.2">{base}</div>
    </div>

    <div style="background:#080b12; border:1px solid #1a1f2e; border-radius:6px; padding:1rem">
      <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:#2e3550; margin-bottom:0.45rem">Annual Bonus</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700;
                  color:#c4c8d8; line-height:1.2">{bonus_val}</div>
      {bonus_note_html}
    </div>

    <div style="background:#0f1a10; border:1px solid #1e3020; border-radius:6px; padding:1rem">
      <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:#2e4a30; margin-bottom:0.45rem">Total Comp</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700;
                  color:#e8c547; line-height:1.2">{total}</div>
    </div>

  </div>

  <!-- Equity -->
  {equity_html}

  <!-- Confidence bar -->
  <div style="border-top:1px solid #1a1f2e; padding-top:1.25rem">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem">
      <span style="font-size:0.65rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                   color:#2e3550">Confidence</span>
      <span style="font-family:'Space Mono',monospace; font-size:0.75rem; color:{col}">{estimate.confidence_pct}%</span>
    </div>
    <div style="height:3px; background:#1a1f2e; border-radius:100px; overflow:hidden; margin-bottom:0.6rem">
      <div style="height:100%; width:{bar_pct}%; background:{col}; border-radius:100px; opacity:0.7"></div>
    </div>
    <div style="font-size:0.78rem; color:#3a4260; line-height:1.55; font-style:italic">
      {estimate.confidence_rationale}
    </div>
  </div>

  <!-- Expandable sections -->
  {factors_html}
  {caveats_html}

</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["Job Description", "Candidate Profile"])

with tab1:
    st.markdown('<p style="color:#3a4260 !important; margin-bottom:1.25rem">For job seekers — paste a job posting URL or the description text to estimate what the role pays.</p>', unsafe_allow_html=True)

    jd_url = st.text_input(
        "Job posting URL",
        placeholder="https://boards.greenhouse.io/...   or   https://www.linkedin.com/jobs/view/...",
        key="jd_url",
    )
    jd_text = st.text_area(
        "Or paste the job description",
        height=200,
        placeholder="Paste the full job description here if you don't have a URL...",
        key="jd_input",
    )
    jd_location = st.text_input(
        "Location",
        placeholder="e.g. London, UK  ·  San Francisco, CA  ·  Remote (US) — leave blank to auto-detect",
        key="jd_location",
    )

    if st.button("Estimate Salary →", key="jd_submit", type="primary", use_container_width=True):
        try:
            content = ""
            if jd_url.strip():
                from src.scraper import fetch_url
                with st.spinner("Fetching job posting…"):
                    content = fetch_url(jd_url.strip())
            else:
                content = jd_text

            if not content.strip():
                st.error("Provide a URL or paste a job description.")
            else:
                with st.spinner("Analysing role and estimating compensation…"):
                    from src.estimator import estimate_from_job_description
                    st.session_state["jd_result"] = estimate_from_job_description(content, jd_location)
        except Exception as e:
            st.error(f"{e}")

    if "jd_result" in st.session_state:
        display_results(st.session_state["jd_result"])


with tab2:
    st.markdown('<p style="color:#3a4260 !important; margin-bottom:1.25rem">For recruiters — paste a LinkedIn profile URL or CV text to estimate what a candidate currently earns.</p>', unsafe_allow_html=True)

    profile_url = st.text_input(
        "LinkedIn profile URL",
        placeholder="https://www.linkedin.com/in/...",
        key="profile_url",
    )
    profile_text = st.text_area(
        "Or paste the candidate profile / CV",
        height=200,
        placeholder="Paste LinkedIn profile text, CV, or employment history here if you don't have a URL...",
        key="profile_input",
    )
    profile_location = st.text_input(
        "Location",
        placeholder="e.g. New York, NY  ·  Dublin, Ireland  ·  leave blank to auto-detect",
        key="profile_location",
    )

    if st.button("Estimate Current Salary →", key="profile_submit", type="primary", use_container_width=True):
        try:
            content = ""
            if profile_url.strip():
                from src.scraper import fetch_url
                with st.spinner("Fetching LinkedIn profile…"):
                    content = fetch_url(profile_url.strip())
            else:
                content = profile_text

            if not content.strip():
                st.error("Provide a URL or paste a candidate profile.")
            else:
                with st.spinner("Reviewing employment history and estimating compensation…"):
                    from src.estimator import estimate_from_candidate_profile
                    st.session_state["profile_result"] = estimate_from_candidate_profile(content, profile_location)
        except Exception as e:
            st.error(f"{e}")

    if "profile_result" in st.session_state:
        display_results(st.session_state["profile_result"])
