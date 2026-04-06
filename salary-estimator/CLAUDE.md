# CompIQ — Salary Estimator

## What This Is

CompIQ is an AI-powered compensation intelligence tool. It estimates salaries for:
- **Job descriptions** — paste or link a posting, get a base/bonus/equity estimate
- **Candidate profiles** — paste or link a LinkedIn profile, get a current earnings estimate

Built with Claude Opus 4.6 (adaptive thinking + structured JSON outputs), Streamlit, Playwright (LinkedIn auth), and httpx/BeautifulSoup (job board scraping).

## Current State (as of April 2026)

Fully functional locally. No production deployment.

**Run it:**
```bash
cd salary-estimator
source .venv/bin/activate
streamlit run app.py
# Opens at http://localhost:8501
```

**Env vars needed** (copy `.env.example` → `.env`):
```
ANTHROPIC_API_KEY=sk-ant-...
LINKEDIN_EMAIL=you@example.com       # optional, for LinkedIn URL scraping
LINKEDIN_PASSWORD=your-password      # optional
```

**One-time setup on a new device:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## File Map

```
app.py            — Streamlit UI, mode switching, results card (custom SVG gauge)
src/estimator.py  — Claude API call, SalaryEstimate pydantic schema, confidence rubric
src/scraper.py    — httpx/BS4 for job boards, Playwright for LinkedIn auth + cookie cache
requirements.txt  — anthropic, streamlit, pydantic, httpx, beautifulsoup4, playwright
.env              — secrets (not committed; rotate API key if .env was ever pushed)
```

## Key Design Decisions

- **Structured outputs** — Claude constrained to `SalaryEstimate` JSON schema via `output_config: json_schema`; Pydantic validates before rendering
- **Adaptive thinking** — `thinking: {type: "adaptive"}` lets Claude reason before answering
- **Streaming** — `.stream().get_final_message()` avoids HTTP timeouts on slow LLM calls
- **Mechanical confidence rubric** — points-based scoring in `estimator.py` (not left to LLM), range ±10–30% depending on confidence tier
- **LinkedIn session persistence** — Playwright saves cookies to `.linkedin_session.json`; first run triggers browser login, subsequent runs reuse session
- **Multi-format scraping** — CSS selector cascade handles Greenhouse, Lever, Workday, Ashby, Indeed, LinkedIn Jobs, company career pages

---

## Next Goal: Chrome Extension (Surface Over LinkedIn)

The plan is to migrate CompIQ from a standalone Streamlit app into a **Chrome extension** that appears contextually when the user is browsing LinkedIn — showing an instant comp estimate without leaving the page.

### Vision

When a user is on:
- A **LinkedIn job posting** → extension injects a panel showing salary estimate for that role
- A **LinkedIn member profile** (recruiter view) → extension shows estimated current earnings for that candidate

No copy-paste, no tab switching. One-click comp intelligence surfaced in context.

---

### What That Involves

#### 1. Architecture Shift

The current app is a monolith (Streamlit front + Python back, same process). The extension needs:

```
Chrome Extension (JS)
  └── content script     — reads the LinkedIn DOM, extracts job/profile data
  └── popup / side panel — renders the comp estimate UI
  └── background worker  — manages API calls, caching, auth token

Backend API (Python/FastAPI)
  └── POST /estimate     — accepts job or profile text, returns SalaryEstimate JSON
  └── Reuses estimator.py logic (Claude API call, pydantic schema)
  └── Hosted (Railway / Fly.io / Render — needs to be always-on)
```

The Claude API call cannot run in the browser — it stays on the backend. The extension sends extracted text to your API; the API calls Claude and returns structured JSON.

#### 2. LinkedIn DOM Scraping (Content Script)

Replace Playwright scraping with a **content script** that reads the already-rendered DOM. LinkedIn is already loaded — no headless browser needed.

**Job posting page** (`/jobs/view/...`):
- Extract: job title, company name, location, job description body
- CSS targets change frequently — build with fallback selectors and version-test regularly

**Profile page** (`/in/...`):
- Extract: name, headline, current role + company, experience list (titles, companies, tenures)
- Avoid scraping PII beyond what's needed for the estimate

Challenges:
- LinkedIn's DOM is heavily obfuscated (generated class names like `ember-view`, `artdeco-*`)
- SPA navigation — content script needs to re-fire on URL change (`pushState` / `popState` listener)
- LinkedIn actively detects and blocks scraping; content scripts run in user context (less risky than headless bots, but still monitor for breakage)

#### 3. Backend API

Thin FastAPI wrapper around the existing `estimator.py`:

```python
# POST /estimate
# body: { "mode": "job"|"profile", "text": "...", "url": "..." }
# returns: SalaryEstimate JSON
```

- Keep `estimator.py` logic unchanged — the prompt, schema, and confidence rubric stay the same
- Add rate limiting (per-user API key or IP) to control Anthropic API spend
- Auth: simplest viable option is a static API key in the extension's storage (can upgrade later)
- CORS: allow only the extension's origin

#### 4. Extension UI (Popup or Side Panel)

Two rendering options:
- **Injected panel** — content script injects a floating div directly into the LinkedIn page (more seamless, higher maintenance)
- **Side panel** — Chrome's built-in side panel API (Chrome 114+, cleaner isolation, slightly less immersive)

Side panel is recommended: avoids style conflicts with LinkedIn's CSS, easier to iterate on.

UI should preserve the existing design language: confidence gauge, comp grid (base / bonus / equity), key factors, caveats.

**Tech choices:**
- Vanilla JS or lightweight framework (Preact/Solid) — avoid React for bundle size in extension context
- Tailwind (with purge) or plain CSS — keep the extension bundle small
- Reuse the existing SVG gauge and card HTML from `app.py`'s results card

#### 5. Auth & Privacy

- No user accounts required in v1 — extension bundles an API key pointing at your backend
- The backend key is obscured (not exposed in source) but is not truly secret in a client-side extension — acceptable for a portfolio/personal tool
- For public distribution: add per-user auth (OAuth / Clerk) before shipping to the Chrome Web Store
- Do not store scraped profile data beyond the request lifecycle

#### 6. Deployment

The backend needs to be always-on (unlike the current local Streamlit app):

| Option | Notes |
|---|---|
| **Railway** | Simplest — push to GitHub, auto-deploy, free tier generous |
| **Fly.io** | Good free tier, easy Dockerfile deploy |
| **Render** | Free tier spins down on inactivity (cold starts) — less ideal |
| **Modal** | Serverless, pay-per-call — good if usage is sporadic |

Recommend Railway or Fly.io for v1. Add a `Dockerfile` and `railway.toml` / `fly.toml`.

#### 7. Build & Package

```
extension/
├── manifest.json          — MV3, permissions: activeTab, storage, sidePanel
├── background.js          — service worker, handles fetch to backend API
├── content.js             — DOM extraction, URL change listener
├── sidepanel/
│   ├── panel.html
│   ├── panel.js
│   └── panel.css
└── icons/
    └── icon-{16,48,128}.png
```

Use **Manifest V3** (MV2 deprecated). Key permissions needed:
- `activeTab` — read current tab DOM
- `storage` — persist API key, cached estimates
- `sidePanel` — render the panel
- `host_permissions: ["https://www.linkedin.com/*"]`

Pack with `zip` for side-loading; submit to Chrome Web Store when ready.

---

### Phased Approach

**Phase 1 — Backend API**
- Wrap `estimator.py` in FastAPI
- Deploy to Railway
- Test with curl / Postman against live job URLs

**Phase 2 — Extension Scaffold + Job Page**
- Build MV3 extension skeleton
- Content script extracts job description on `/jobs/view/` pages
- Side panel calls backend, renders estimate
- Load unpacked in Chrome for development

**Phase 3 — Profile Page**
- Extend content script to handle `/in/` profile pages
- Extract experience, pass to backend in profile mode
- Render candidate earnings estimate in side panel

**Phase 4 — Polish**
- Match existing CompIQ visual design (gauge, comp grid)
- Handle SPA navigation (URL change listener)
- Error states (rate limit, scrape failure, low confidence)
- Icon, name, Chrome Web Store listing

---

### Outstanding Before Switching Devices

- [ ] Rotate the Anthropic API key (`.env` may have been in git history — check with `git log --all -- .env`)
- [ ] Confirm `.venv/` is in `.gitignore`
- [ ] Verify `.linkedin_session.json` is in `.gitignore` (contains auth cookies)
- [ ] Push latest working state to GitHub (`git push origin main`)
