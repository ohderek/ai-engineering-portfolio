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

## Stack

| Layer | Tools |
|-------|-------|
| LLM APIs | Anthropic (Claude), Ollama (Llama, CodeLlama) |
| Validation | Pydantic v2 |
| CLI | Typer |
| Terminal UI | Rich |
| Language | Python 3.13 |
