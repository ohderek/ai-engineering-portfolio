"""
Salary Estimator — Streamlit UI
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CompIQ", page_icon="◈", layout="centered")

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

/* ── Base & background ────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif !important;
}
.stApp {
    background-color: #060d1a !important;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% 0%, rgba(0,180,255,0.07) 0%, transparent 70%),
        linear-gradient(rgba(0,180,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,180,255,0.025) 1px, transparent 1px) !important;
    background-size: auto, 48px 48px, 48px 48px !important;
}
.block-container {
    max-width: 760px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 5rem !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Text defaults ────────────────────────────────── */
p, li, span, div { color: #8ba4c0; }

/* ── Inputs ───────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea {
    background: rgba(6, 18, 36, 0.8) !important;
    border: 1px solid rgba(0,180,255,0.12) !important;
    color: #c8dff0 !important;
    border-radius: 6px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    caret-color: #00cfff !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(0,207,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,207,255,0.06), 0 0 16px rgba(0,207,255,0.06) !important;
    outline: none !important;
}
.stTextInput label,
.stTextArea label {
    color: rgba(0,180,255,0.45) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
::placeholder { color: rgba(0,150,220,0.2) !important; }

/* ── Button ───────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00cfff 0%, #0090e0 100%) !important;
    color: #030912 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 0 20px rgba(0,207,255,0.2) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #33daff 0%, #00aaf0 100%) !important;
    box-shadow: 0 0 32px rgba(0,207,255,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Tabs ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,180,255,0.1) !important;
    gap: 0 !important;
    margin-bottom: 1.75rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(0,150,200,0.35) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    padding: 0.75rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    text-transform: uppercase !important;
    transition: color 0.15s !important;
}
.stTabs [aria-selected="true"] {
    color: #00cfff !important;
    border-bottom: 2px solid #00cfff !important;
    text-shadow: 0 0 12px rgba(0,207,255,0.4) !important;
}

/* ── Spinner ──────────────────────────────────────── */
.stSpinner p { color: rgba(0,180,255,0.4) !important; font-size: 0.78rem !important; }

/* ── Alerts ───────────────────────────────────────── */
.stAlert {
    background: rgba(6,18,36,0.9) !important;
    border: 1px solid rgba(0,180,255,0.15) !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<div style="margin-bottom:2.5rem; padding-bottom:1.75rem; border-bottom:1px solid rgba(0,180,255,0.1)">
  <div style="font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800;
              letter-spacing:-0.04em; color:#e0f0ff; line-height:1; margin-bottom:0.5rem">
    Comp<span style="color:#00cfff; text-shadow:0 0 24px rgba(0,207,255,0.6), 0 0 48px rgba(0,207,255,0.2)">IQ</span>
  </div>
  <div style="font-size:0.68rem; color:rgba(0,160,210,0.45); letter-spacing:0.14em;
              text-transform:uppercase; font-family:'Instrument Sans',sans-serif; font-weight:600">
    Compensation intelligence &nbsp;/&nbsp; Powered by Claude
  </div>
</div>
""", unsafe_allow_html=True)


# ── Results card ───────────────────────────────────────────────────────────────

def _conf_props(pct: int):
    if pct >= 80:
        return "#00ff99", "rgba(0,255,153,0.07)", "rgba(0,255,153,0.2)", "High confidence"
    if pct >= 60:
        return "#fbbf24", "rgba(251,191,36,0.07)", "rgba(251,191,36,0.2)", "Medium confidence"
    return "#ff4d6d", "rgba(255,77,109,0.07)", "rgba(255,77,109,0.2)", "Low confidence"


def _items_html(items: list[str], icon: str, label: str) -> str:
    if not items:
        return ""
    lis = "".join(
        f'<li style="padding:0.3rem 0; color:rgba(140,180,210,0.7); '
        f'border-bottom:1px solid rgba(0,180,255,0.06); font-size:0.82rem">{i}</li>'
        for i in items
    )
    return f"""
<details style="margin-top:0.75rem">
  <summary style="cursor:pointer; font-size:0.65rem; font-weight:600; letter-spacing:0.12em;
                  text-transform:uppercase; color:rgba(0,160,210,0.4); padding:0.65rem 0;
                  list-style:none; user-select:none; display:flex; align-items:center; gap:0.4rem;
                  font-family:'Instrument Sans',sans-serif">
    <span>{icon}</span> {label}
  </summary>
  <ul style="margin:0.4rem 0 0; padding:0; list-style:none; font-family:'Instrument Sans',sans-serif">
    {lis}
  </ul>
</details>"""


def display_results(estimate) -> None:
    col, bg, bdr, conf_label = _conf_props(estimate.confidence_pct)

    base  = fmt_range(estimate.base_salary.low,  estimate.base_salary.high,  estimate.currency)
    total = fmt_range(estimate.total_compensation.low, estimate.total_compensation.high, estimate.currency)

    if estimate.annual_bonus:
        bonus_val = fmt_range(estimate.annual_bonus.low, estimate.annual_bonus.high, estimate.currency)
    else:
        bonus_val = "—"
    bonus_note = estimate.bonus_note or ("" if estimate.annual_bonus else "Not typical")

    equity_html = ""
    if estimate.equity_note:
        equity_html = f"""
<div style="background:rgba(0,10,24,0.6); border:1px solid rgba(0,180,255,0.1);
            border-radius:6px; padding:0.65rem 1rem; margin-bottom:1.25rem;
            display:flex; align-items:center; gap:0.75rem">
  <span style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
               color:rgba(0,160,210,0.4); white-space:nowrap; font-family:'Instrument Sans',sans-serif">Equity</span>
  <span style="font-size:0.84rem; color:rgba(140,180,210,0.8); font-family:'Instrument Sans',sans-serif">{estimate.equity_note}</span>
</div>"""

    st.markdown(f"""
<div style="background:rgba(8,16,32,0.85); border:1px solid rgba(0,180,255,0.14);
            border-radius:10px; padding:1.75rem; margin-top:1.5rem;
            box-shadow:0 0 40px rgba(0,150,255,0.04), inset 0 1px 0 rgba(0,207,255,0.06);
            font-family:'Instrument Sans',sans-serif">

  <!-- Header -->
  <div style="display:flex; justify-content:space-between; align-items:flex-start;
              margin-bottom:1.5rem; padding-bottom:1.5rem; border-bottom:1px solid rgba(0,180,255,0.08)">
    <div>
      <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800;
                  letter-spacing:-0.02em; color:#d8ecff; line-height:1.2; margin-bottom:0.35rem">
        {estimate.role_title}
      </div>
      <div style="font-size:0.73rem; color:rgba(0,160,210,0.45); letter-spacing:0.04em">
        ◎ {estimate.location} &nbsp;·&nbsp; {estimate.seniority_level}
      </div>
    </div>
    <div style="background:{bg}; border:1px solid {bdr}; border-radius:8px;
                padding:0.4rem 0.9rem; text-align:center; white-space:nowrap; flex-shrink:0;
                box-shadow:0 0 16px {bdr}">
      <div style="font-family:'Space Mono',monospace; font-size:1.1rem; font-weight:700;
                  color:{col}; line-height:1; text-shadow:0 0 12px {col}40">{estimate.confidence_pct}%</div>
      <div style="font-size:0.58rem; color:{col}; opacity:0.7; letter-spacing:0.08em;
                  text-transform:uppercase; margin-top:0.18rem">{conf_label}</div>
    </div>
  </div>

  <!-- Comp grid -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.7rem; margin-bottom:1.25rem">

    <div style="background:rgba(0,10,24,0.6); border:1px solid rgba(0,180,255,0.08);
                border-radius:6px; padding:1rem">
      <div style="font-size:0.6rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:rgba(0,160,210,0.35); margin-bottom:0.45rem">Base Salary</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700;
                  color:#b8d4ee; line-height:1.2">{base}</div>
    </div>

    <div style="background:rgba(0,10,24,0.6); border:1px solid rgba(0,180,255,0.08);
                border-radius:6px; padding:1rem">
      <div style="font-size:0.6rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:rgba(0,160,210,0.35); margin-bottom:0.45rem">Annual Bonus</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700;
                  color:#b8d4ee; line-height:1.2">{bonus_val}</div>
      <div style="font-size:0.68rem; color:rgba(0,140,180,0.4); margin-top:0.3rem; font-style:italic">{bonus_note}</div>
    </div>

    <div style="background:rgba(0,20,40,0.7); border:1px solid rgba(0,207,255,0.2);
                border-radius:6px; padding:1rem;
                box-shadow:0 0 20px rgba(0,207,255,0.04), inset 0 1px 0 rgba(0,207,255,0.08)">
      <div style="font-size:0.6rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                  color:rgba(0,207,255,0.4); margin-bottom:0.45rem">Total Comp</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700; color:#00cfff;
                  line-height:1.2; text-shadow:0 0 12px rgba(0,207,255,0.3)">{total}</div>
    </div>

  </div>

  {equity_html}

  <!-- Confidence bar -->
  <div style="border-top:1px solid rgba(0,180,255,0.08); padding-top:1.2rem">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.45rem">
      <span style="font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
                   color:rgba(0,160,210,0.35); font-family:'Instrument Sans',sans-serif">Confidence</span>
      <span style="font-family:'Space Mono',monospace; font-size:0.72rem; color:{col};
                   text-shadow:0 0 8px {col}60">{estimate.confidence_pct}%</span>
    </div>
    <div style="height:2px; background:rgba(0,180,255,0.08); border-radius:100px;
                overflow:hidden; margin-bottom:0.65rem">
      <div style="height:100%; width:{estimate.confidence_pct}%; background:linear-gradient(90deg,{col}90,{col});
                  border-radius:100px; box-shadow:0 0 8px {col}80"></div>
    </div>
    <div style="font-size:0.77rem; color:rgba(100,150,190,0.65); line-height:1.55; font-style:italic">
      {estimate.confidence_rationale}
    </div>
  </div>

  {_items_html(estimate.key_factors, "◦", "Key factors")}
  {_items_html(estimate.caveats, "△", "Caveats")}

</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["Job Description", "Candidate Profile"])

with tab1:
    st.markdown('<p style="color:rgba(0,150,200,0.4) !important; margin-bottom:1.25rem; font-size:0.82rem">For job seekers — paste a job posting URL or the description text to estimate what the role pays.</p>', unsafe_allow_html=True)

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
    st.markdown('<p style="color:rgba(0,150,200,0.4) !important; margin-bottom:1.25rem; font-size:0.82rem">For recruiters — paste a LinkedIn profile URL or CV text to estimate what a candidate currently earns.</p>', unsafe_allow_html=True)

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
