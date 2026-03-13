# Setup Guide

This project runs with either the Anthropic API (easiest) or Ollama (fully open source, local).

---

## Option A — Anthropic API

### Step 1 — Create a virtual environment

```bash
cd ai-data-assistant
python3 -m venv .venv
source .venv/bin/activate
```

Run `source .venv/bin/activate` each time you open a new terminal session.

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

Installs: `anthropic`, `pydantic`, `rich`, `typer`, `python-dotenv`.

### Step 3 — Set up your API key

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Get a free key at **console.anthropic.com** — new accounts receive $5 of free credits.

### Step 4 — Run the features

```bash
# SQL code review (streaming output)
python main.py review examples/fct_orders.sql

# Generate dbt schema.yml documentation
python main.py docs examples/dim_customers.sql --model dim_customers

# Interactive chat
python main.py chat
```

---

## Option B — Ollama (fully open source, no API key)

Runs a local LLM on your machine. No key, no cost, no data leaving your machine.

### Step 1 — Install Ollama

```bash
brew install ollama
```

### Step 2 — Pull a model

```bash
ollama pull llama3.2      # ~2GB — fast, good for chat
ollama pull codellama     # ~4GB — better for SQL tasks
```

### Step 3 — Add the openai package

```bash
pip install openai
```

### Step 4 — Swap the client

Replace `src/client.py` with this version:

```python
from openai import OpenAI

MODEL = "llama3.2"  # or "codellama"

def get_client():
    return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def stream_response(messages, system="", max_tokens=2048):
    client = get_client()
    full_text = ""
    with client.chat.completions.stream(
        model=MODEL,
        messages=[{"role": "system", "content": system}, *messages],
        max_tokens=max_tokens,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text
    print()
    return full_text
```

### Step 5 — Start Ollama and run

```bash
ollama serve          # keep running in a separate terminal
python main.py review examples/fct_orders.sql
```

---

## Open source stack summary

| Component | Tool | Open source? |
|-----------|------|-------------|
| LLM (API route) | Claude via Anthropic SDK | SDK yes, model no |
| LLM (local route) | Llama 3.2 via Ollama | Fully open source |
| Output validation | Pydantic v2 | Yes |
| CLI framework | Typer | Yes |
| Terminal UI | Rich | Yes |
| Language | Python 3.13 | Yes |
