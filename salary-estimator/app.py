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
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}
.stApp {
    background: #f0f4fa !important;
}
.block-container {
    max-width: 780px !important;
    padding-top: 0 !important;
    padding-bottom: 5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f2 !important;
    color: #1a2540 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #3b6ef5 !important;
    box-shadow: 0 0 0 3px rgba(59,110,245,0.1) !important;
    outline: none !important;
}
.stTextInput label,
.stTextArea label {
    color: #64748b !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}
::placeholder { color: #c8d3e8 !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #3b6ef5 0%, #2251d3 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 4px 14px rgba(59,110,245,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f7ef7 0%, #3060e8 100%) !important;
    box-shadow: 0 6px 20px rgba(59,110,245,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid #e2e8f2 !important;
    gap: 0 !important;
    margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    padding: 0.75rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    text-transform: uppercase !important;
    transition: color 0.15s !important;
}
.stTabs [aria-selected="true"] {
    color: #3b6ef5 !important;
    border-bottom: 2px solid #3b6ef5 !important;
}

/* Spinner */
.stSpinner p { color: #94a3b8 !important; font-size: 0.8rem !important; }

/* Alerts */
.stAlert {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f2 !important;
    border-radius: 8px !important;
    color: #1a2540 !important;
}

p, li { color: #64748b !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

<div style="
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 2rem;
  height: 240px;
  background-color: #1a2540;
  background-image: url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1400&h=600&fit=crop&q=80&auto=format');
  background-size: cover;
  background-position: center 30%;
">
  <div style="
    position: absolute; inset: 0;
    background: linear-gradient(120deg, rgba(10,18,50,0.88) 0%, rgba(30,50,120,0.7) 60%, rgba(59,110,245,0.4) 100%);
  "></div>
  <div style="position:relative; z-index:1; padding: 2.25rem 2.5rem; height:100%;
              display:flex; flex-direction:column; justify-content:space-between">
    <div>
      <div style="font-family:'Bricolage Grotesque',sans-serif; font-size:2.6rem; font-weight:800;
                  color:#ffffff; letter-spacing:-0.04em; line-height:1; margin-bottom:0.5rem">
        Comp<span style="color:#6fa3ff">IQ</span>
      </div>
      <div style="font-size:0.85rem; color:rgba(255,255,255,0.55); letter-spacing:0.04em;
                  font-family:'DM Sans',sans-serif">
        Know your worth. Know your candidate.
      </div>
    </div>
    <div style="display:flex; gap:2rem">
      <div>
        <div style="font-family:'DM Mono',monospace; font-size:1.4rem; font-weight:500; color:#ffffff">≈ $0</div>
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.4); letter-spacing:0.06em; text-transform:uppercase; margin-top:0.1rem">hidden in every offer</div>
      </div>
      <div>
        <div style="font-family:'DM Mono',monospace; font-size:1.4rem; font-weight:500; color:#ffffff">AI</div>
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.4); letter-spacing:0.06em; text-transform:uppercase; margin-top:0.1rem">powered by Claude</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Results card ───────────────────────────────────────────────────────────────

def _conf_props(pct: int):
    if pct >= 80:
        return "#059669", "#ecfdf5", "#a7f3d0", "#d1fae5", "High"
    if pct >= 60:
        return "#d97706", "#fffbeb", "#fcd34d", "#fef3c7", "Medium"
    return "#dc2626", "#fef2f2", "#fca5a5", "#fee2e2", "Low"


def _items_html(items: list[str], label: str, icon: str) -> str:
    if not items:
        return ""
    lis = "".join(
        f'<li style="padding:0.35rem 0; color:#64748b; border-bottom:1px solid #f1f5f9; font-size:0.82rem; font-family:DM Sans,sans-serif">{i}</li>'
        for i in items
    )
    return f"""
<details style="margin-top:0.6rem">
  <summary style="cursor:pointer; font-size:0.68rem; font-weight:600; letter-spacing:0.1em;
                  text-transform:uppercase; color:#94a3b8; padding:0.6rem 0; list-style:none;
                  user-select:none; font-family:'DM Sans',sans-serif">
    {icon} &nbsp;{label}
  </summary>
  <ul style="margin:0.4rem 0 0; padding:0; list-style:none">{lis}</ul>
</details>"""


def display_results(estimate) -> None:
    fg, bg_light, bar_col, pill_bg, conf_label = _conf_props(estimate.confidence_pct)

    base  = fmt_range(estimate.base_salary.low,  estimate.base_salary.high,  estimate.currency)
    total = fmt_range(estimate.total_compensation.low, estimate.total_compensation.high, estimate.currency)
    bonus_val  = fmt_range(estimate.annual_bonus.low, estimate.annual_bonus.high, estimate.currency) if estimate.annual_bonus else "—"
    bonus_note = estimate.bonus_note or ("" if estimate.annual_bonus else "Not typical for this role")

    equity_html = ""
    if estimate.equity_note:
        equity_html = f"""
<div style="background:#f8faff; border:1.5px solid #e8eeff; border-radius:8px;
            padding:0.75rem 1rem; margin-bottom:1.25rem; display:flex; align-items:center; gap:0.75rem">
  <span style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
               color:#94a3b8; white-space:nowrap; font-family:'DM Sans',sans-serif">Equity</span>
  <span style="font-size:0.84rem; color:#475569; font-family:'DM Sans',sans-serif">{estimate.equity_note}</span>
</div>"""

    st.markdown(f"""
<div style="background:#ffffff; border:1.5px solid #e8eef8; border-radius:12px;
            padding:1.75rem; margin-top:1.5rem;
            box-shadow: 0 4px 24px rgba(59,110,245,0.07), 0 1px 3px rgba(0,0,0,0.04)">

  <!-- Header -->
  <div style="display:flex; justify-content:space-between; align-items:flex-start;
              margin-bottom:1.5rem; padding-bottom:1.5rem; border-bottom:1.5px solid #f1f5f9">
    <div>
      <div style="font-family:'Bricolage Grotesque',sans-serif; font-size:1.3rem; font-weight:800;
                  letter-spacing:-0.02em; color:#0f1a35; line-height:1.2; margin-bottom:0.3rem">
        {estimate.role_title}
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:0.02em; font-family:'DM Sans',sans-serif">
        📍 {estimate.location} &nbsp;·&nbsp; {estimate.seniority_level}
      </div>
    </div>
    <div style="background:{pill_bg}; border:1.5px solid {bar_col}; border-radius:10px;
                padding:0.45rem 0.9rem; text-align:center; flex-shrink:0">
      <div style="font-family:'DM Mono',monospace; font-size:1.1rem; font-weight:500;
                  color:{fg}; line-height:1">{estimate.confidence_pct}%</div>
      <div style="font-size:0.6rem; color:{fg}; opacity:0.8; letter-spacing:0.06em;
                  text-transform:uppercase; margin-top:0.15rem; font-family:'DM Sans',sans-serif">{conf_label}</div>
    </div>
  </div>

  <!-- Comp grid -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.75rem; margin-bottom:1.25rem">

    <div style="background:#f8faff; border:1.5px solid #e8eef8; border-radius:8px; padding:1rem">
      <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                  color:#94a3b8; margin-bottom:0.45rem; font-family:'DM Sans',sans-serif">Base Salary</div>
      <div style="font-family:'DM Mono',monospace; font-size:0.95rem; font-weight:500;
                  color:#1e3a5f; line-height:1.2">{base}</div>
    </div>

    <div style="background:#f8faff; border:1.5px solid #e8eef8; border-radius:8px; padding:1rem">
      <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                  color:#94a3b8; margin-bottom:0.45rem; font-family:'DM Sans',sans-serif">Annual Bonus</div>
      <div style="font-family:'DM Mono',monospace; font-size:0.95rem; font-weight:500;
                  color:#1e3a5f; line-height:1.2">{bonus_val}</div>
      <div style="font-size:0.68rem; color:#94a3b8; margin-top:0.3rem; font-style:italic;
                  font-family:'DM Sans',sans-serif">{bonus_note}</div>
    </div>

    <div style="background:linear-gradient(135deg, #3b6ef5 0%, #2251d3 100%); border-radius:8px; padding:1rem;
                box-shadow: 0 4px 14px rgba(59,110,245,0.25)">
      <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                  color:rgba(255,255,255,0.6); margin-bottom:0.45rem; font-family:'DM Sans',sans-serif">Total Comp</div>
      <div style="font-family:'DM Mono',monospace; font-size:0.95rem; font-weight:500;
                  color:#ffffff; line-height:1.2">{total}</div>
    </div>

  </div>

  {equity_html}

  <!-- Confidence bar -->
  <div style="border-top:1.5px solid #f1f5f9; padding-top:1.2rem">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.45rem">
      <span style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                   color:#94a3b8; font-family:'DM Sans',sans-serif">Confidence</span>
      <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:{fg}">{estimate.confidence_pct}%</span>
    </div>
    <div style="height:5px; background:#f1f5f9; border-radius:100px; overflow:hidden; margin-bottom:0.65rem">
      <div style="height:100%; width:{estimate.confidence_pct}%; background:{fg}; border-radius:100px; opacity:0.8"></div>
    </div>
    <div style="font-size:0.78rem; color:#64748b; line-height:1.6; font-style:italic;
                font-family:'DM Sans',sans-serif">
      {estimate.confidence_rationale}
    </div>
  </div>

  {_items_html(estimate.key_factors, "Key Factors", "◦")}
  {_items_html(estimate.caveats, "Caveats", "△")}

</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["Job Description", "Candidate Profile"])

with tab1:
    # Context image strip
    st.markdown("""
    <div style="display:flex; align-items:center; gap:1rem; background:#ffffff; border:1.5px solid #e8eef8;
                border-radius:10px; padding:0.85rem 1rem; margin-bottom:1.5rem;
                box-shadow:0 1px 4px rgba(59,110,245,0.06)">
      <div style="width:54px; height:54px; border-radius:8px; overflow:hidden; flex-shrink:0;
                  background:#e8eef8">
        <img src="https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=120&h=120&fit=crop&q=80&auto=format"
             style="width:100%; height:100%; object-fit:cover" />
      </div>
      <div>
        <div style="font-family:'Bricolage Grotesque',sans-serif; font-weight:700; font-size:0.92rem; color:#0f1a35">
          For Job Seekers
        </div>
        <div style="font-size:0.78rem; color:#64748b; margin-top:0.1rem; font-family:'DM Sans',sans-serif">
          Paste a job posting URL or description — know the number before you negotiate.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    jd_url = st.text_input(
        "Job posting URL",
        placeholder="https://boards.greenhouse.io/...   or   https://www.linkedin.com/jobs/view/...",
        key="jd_url",
    )
    jd_text = st.text_area(
        "Or paste the job description",
        height=180,
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
    # Context image strip
    st.markdown("""
    <div style="display:flex; align-items:center; gap:1rem; background:#ffffff; border:1.5px solid #e8eef8;
                border-radius:10px; padding:0.85rem 1rem; margin-bottom:1.5rem;
                box-shadow:0 1px 4px rgba(59,110,245,0.06)">
      <div style="width:54px; height:54px; border-radius:8px; overflow:hidden; flex-shrink:0;
                  background:#e8eef8">
        <img src="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=120&h=120&fit=crop&q=80&auto=format"
             style="width:100%; height:100%; object-fit:cover" />
      </div>
      <div>
        <div style="font-family:'Bricolage Grotesque',sans-serif; font-weight:700; font-size:0.92rem; color:#0f1a35">
          For Recruiters
        </div>
        <div style="font-size:0.78rem; color:#64748b; margin-top:0.1rem; font-family:'DM Sans',sans-serif">
          Paste a LinkedIn profile or CV — estimate what a candidate currently earns before making an offer.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    profile_url = st.text_input(
        "LinkedIn profile URL",
        placeholder="https://www.linkedin.com/in/...",
        key="profile_url",
    )
    profile_text = st.text_area(
        "Or paste the candidate profile / CV",
        height=180,
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
