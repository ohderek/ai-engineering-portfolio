# AI Engineering Portfolio

A collection of projects demonstrating how to integrate pre-trained LLMs into real-world data engineering workflows — covering API integration, prompt engineering, structured outputs, and local open source model deployment.

---

## Projects

### [ai-data-assistant](./ai-data-assistant)

A command-line tool for data engineers that showcases a typical AI engineering pipeline:

```
Input (SQL / question)
    │
    ▼
Prompt Engineering Layer   ← system prompts, few-shot examples
    │
    ▼
LLM API (Claude / Ollama)  ← streaming, multi-turn, structured output
    │
    ▼
Structured Output           ← validated Pydantic models, YAML, review feedback
```

**Features:**
- `review` — Stream a code review of any SQL model
- `docs` — Generate dbt `schema.yml` documentation from SQL
- `chat` — Multi-turn interactive data engineering assistant

**Key techniques:** system prompts · few-shot examples · structured outputs · streaming · conversation history

**Runs with:** Anthropic API (Claude) or Ollama (fully open source, local)

→ [Setup guide](./ai-data-assistant/SETUP.md)

---

### [support-rag-bot](./support-rag-bot)

A Retrieval-Augmented Generation (RAG) pipeline that turns any document or folder of documents into a queryable support bot. Ingests once, then answers plain-English questions grounded in the content.

**Features:**
- `ingest` — Load, chunk, embed, and store a document or folder of `.md` files in a local vector database
- `ask` — Ask a single question with optional source chunk citations
- `chat` — Interactive Q&A session via CLI
- Streamlit UI — browser-based chat interface (`streamlit run app.py`)

**Key techniques:** document chunking · local embeddings (HuggingFace) · vector store (Chroma) · RAG · LangChain LCEL · prompt templates

**Runs with:** Anthropic API for the LLM; HuggingFace embeddings run locally (no key needed)

→ [README](./support-rag-bot/README.md)

---

### [salary-estimator](./salary-estimator)

A hypothetical compensation intelligence tool that estimates salary ranges for job postings and candidate profiles. Accepts URLs or pasted text and returns structured estimates with confidence scores.

**Features:**
- Paste a job posting URL (Greenhouse, Lever, Workday, Indeed, LinkedIn Jobs) or text → estimate what the role pays
- Paste a LinkedIn profile URL or CV text → estimate what a candidate currently earns
- Location auto-detected or manually entered
- Returns base salary, bonus, equity, and total comp ranges with a confidence score and rationale

**Key techniques:** structured outputs with JSON schema · adaptive thinking · Playwright browser automation · httpx + BeautifulSoup scraping · Pydantic validation

**Runs with:** Anthropic API (Claude Opus 4.6)

→ [README](./salary-estimator/README.md)

---

## Stack

| Layer | Tools |
|-------|-------|
| LLM APIs | Anthropic (Claude), Ollama (Llama, CodeLlama) |
| Orchestration | LangChain (LCEL, retrievers, prompt templates) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local) |
| Vector store | Chroma (local, open source) |
| Validation | Pydantic v2 |
| CLI | Typer |
| Terminal UI | Rich |
| Web UI | Streamlit |
| Web scraping | httpx + BeautifulSoup4 |
| Browser automation | Playwright (headless Chromium) |
| Language | Python 3.13 |
