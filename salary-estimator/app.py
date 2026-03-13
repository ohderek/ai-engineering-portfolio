"""
Salary Estimator — Streamlit UI

Two modes:
  📋 Job Description  — for job seekers estimating what a role pays
  👤 Candidate Profile — for recruiters estimating what a candidate earns

Usage:
  streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Salary Estimator",
    page_icon="💰",
    layout="centered",
)

st.title("💰 Salary Estimator")
st.caption("Powered by Claude — estimate compensation for any role or candidate.")


# ── Helpers ────────────────────────────────────────────────────────────────────

CURRENCY_SYMBOLS = {
    "USD": "$", "GBP": "£", "EUR": "€",
    "CAD": "CA$", "AUD": "A$", "SGD": "S$",
}

def fmt(amount: int, currency: str = "USD") -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency + "\u00a0")
    if amount >= 1_000:
        return f"{symbol}{amount // 1000}k"
    return f"{symbol}{amount:,}"

def fmt_range(low: int, high: int, currency: str) -> str:
    return f"{fmt(low, currency)} – {fmt(high, currency)}"

def confidence_badge(pct: int) -> str:
    if pct >= 80:
        return f"🟢 {pct}% confidence"
    elif pct >= 60:
        return f"🟡 {pct}% confidence"
    return f"🔴 {pct}% confidence"

def resolve_input(url: str, text: str, spinner_msg: str) -> str:
    """Return text content from URL (if provided) or fall back to pasted text."""
    if url.strip():
        from src.scraper import fetch_url
        with st.spinner(spinner_msg):
            return fetch_url(url.strip())
    return text


def display_results(estimate) -> None:
    st.divider()

    col_title, col_conf = st.columns([3, 1])
    with col_title:
        st.subheader(estimate.role_title)
        st.caption(f"📍 {estimate.location}  •  {estimate.seniority_level}")
    with col_conf:
        st.markdown(f"### {confidence_badge(estimate.confidence_pct)}")

    st.markdown("#### Compensation Breakdown")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Base Salary",
            fmt_range(estimate.base_salary.low, estimate.base_salary.high, estimate.currency),
        )
    with c2:
        if estimate.annual_bonus:
            st.metric(
                "Annual Bonus",
                fmt_range(estimate.annual_bonus.low, estimate.annual_bonus.high, estimate.currency),
                help=estimate.bonus_note,
            )
        else:
            st.metric("Annual Bonus", "—", help=estimate.bonus_note or "Not typical for this role")
    with c3:
        st.metric(
            "Total Comp",
            fmt_range(estimate.total_compensation.low, estimate.total_compensation.high, estimate.currency),
        )

    if estimate.equity_note:
        st.info(f"**Equity:** {estimate.equity_note}")

    st.divider()
    st.progress(estimate.confidence_pct / 100, text=f"**Confidence: {estimate.confidence_pct}%**")
    st.caption(estimate.confidence_rationale)

    with st.expander("Key factors considered"):
        for factor in estimate.key_factors:
            st.write(f"• {factor}")

    if estimate.caveats:
        with st.expander("⚠️ Caveats & limitations"):
            for caveat in estimate.caveats:
                st.write(f"• {caveat}")


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📋 Job Description", "👤 Candidate Profile"])

with tab1:
    st.write("**For job seekers** — paste a job posting URL or the description text to estimate what the role pays.")

    jd_url = st.text_input(
        "Job posting URL",
        placeholder="https://boards.greenhouse.io/...  or  https://www.linkedin.com/jobs/view/...",
        key="jd_url",
    )

    jd_text = st.text_area(
        "Or paste the job description",
        height=220,
        placeholder="Paste the full job description here if you don't have a URL...",
        key="jd_input",
    )
    jd_location = st.text_input(
        "Location",
        placeholder="e.g. London, UK  •  San Francisco, CA  •  Remote (US) — leave blank to auto-detect",
        key="jd_location",
    )

    if st.button("Estimate Salary", key="jd_submit", type="primary", use_container_width=True):
        try:
            content = resolve_input(jd_url, jd_text, "Fetching job posting…")
            if not content.strip():
                st.error("Provide a URL or paste a job description.")
            else:
                with st.spinner("Analysing role and estimating compensation…"):
                    from src.estimator import estimate_from_job_description
                    st.session_state["jd_result"] = estimate_from_job_description(content, jd_location)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    if "jd_result" in st.session_state:
        display_results(st.session_state["jd_result"])


with tab2:
    st.write("**For recruiters** — paste a LinkedIn profile URL or CV text to estimate what a candidate currently earns.")

    profile_url = st.text_input(
        "LinkedIn profile URL",
        placeholder="https://www.linkedin.com/in/...",
        key="profile_url",
    )

    profile_text = st.text_area(
        "Or paste the candidate profile / CV",
        height=220,
        placeholder="Paste LinkedIn profile text, CV, or employment history here if you don't have a URL...",
        key="profile_input",
    )
    profile_location = st.text_input(
        "Location",
        placeholder="e.g. New York, NY  •  Dublin, Ireland  •  leave blank to auto-detect",
        key="profile_location",
    )

    if st.button("Estimate Current Salary", key="profile_submit", type="primary", use_container_width=True):
        try:
            content = resolve_input(profile_url, profile_text, "Fetching LinkedIn profile…")
            if not content.strip():
                st.error("Provide a URL or paste a candidate profile.")
            else:
                with st.spinner("Reviewing employment history and estimating compensation…"):
                    from src.estimator import estimate_from_candidate_profile
                    st.session_state["profile_result"] = estimate_from_candidate_profile(content, profile_location)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    if "profile_result" in st.session_state:
        display_results(st.session_state["profile_result"])
