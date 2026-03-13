# AI Data Assistant

> A showcase of a typical AI engineering data pipeline — taking raw inputs (SQL models, user queries), processing them through an LLM with carefully engineered prompts, and returning structured, actionable outputs.

AI engineering is fundamentally about integrating pre-trained models into workflows that deliver business value. This project demonstrates that pattern end-to-end in a data engineering context:

```
Input (SQL / question)
    │
    ▼
Prompt Engineering Layer   ← system prompts, few-shot examples
    │
    ▼
LLM API (Claude Opus 4.6)  ← streaming, multi-turn, structured output
    │
    ▼
Structured Output           ← validated Pydantic models, YAML, review feedback
    │
    ▼
Action (fix SQL / publish docs / answer question)
```

### Core AI engineering skills demonstrated

| Skill | How it's shown |
|-------|----------------|
| LLM API integration | Anthropic Python SDK — streaming, single calls, multi-turn |
| Prompt engineering | System prompts, few-shot examples, structured outputs |
| Output validation | Pydantic v2 — guaranteed schema compliance, no string parsing |
| Agentic patterns | Stateful multi-turn chat with full conversation history |

### Why not LangChain?

LangChain is a popular abstraction layer for chaining LLM calls, but for focused use cases like this it adds complexity without much benefit. This project uses the **Anthropic SDK directly** — giving full visibility into every API call, prompt, and response. That's intentional: understanding what's happening at the SDK level is the foundation before layering on frameworks like LangChain or LlamaIndex. Both are worth knowing; the raw SDK is where to start.

---

## What it does

A command-line tool for data engineers with three AI-powered features:

**`review`** — Stream a code review of any SQL model, flagging performance issues, correctness bugs, and style violations.

**`docs`** — Generate `schema.yml` dbt documentation from a SQL file using few-shot examples and structured output (Pydantic).

**`chat`** — Multi-turn interactive assistant for SQL, dbt, Snowflake, Airflow, and Prefect questions.

---

## Prompt engineering techniques

### 1. System prompts (`src/prompts.py`)
Each feature has a tailored system prompt that gives the model a persona and explicit output rules — the single highest-leverage prompt engineering technique.

```python
SQL_REVIEWER_SYSTEM = """You are a senior data engineer specializing in SQL best practices...
Format your feedback as numbered issues with severity [HIGH / MEDIUM / LOW]..."""
```

### 2. Few-shot examples (`src/doc_generator.py`)
Before the real SQL is sent, the model sees a worked example of exactly the output format we want. This dramatically reduces hallucinations and format drift.

```python
messages = [
    *FEW_SHOT_DOC_EXAMPLES,   # show Claude what "good" looks like first
    {"role": "user", "content": f"Generate docs for:\n{sql}"},
]
```

### 3. Structured outputs (`src/doc_generator.py`)
Using `client.messages.parse()` with a Pydantic model guarantees the response matches our schema — no string parsing, no surprises.

```python
class ModelDoc(BaseModel):
    model_name: str
    description: str
    columns: list[ColumnDoc]
    yaml_output: str

response = client.messages.parse(..., output_format=ModelDoc)
doc: ModelDoc = response.parsed_output  # fully validated
```

---

## Setup

```bash
git clone https://github.com/dereko/ai-data-assistant
cd ai-data-assistant
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
```

## Usage

```bash
# Review a SQL file for issues
python main.py review examples/fct_orders.sql

# Generate dbt schema.yml documentation
python main.py docs examples/dim_customers.sql --model dim_customers

# Start an interactive chat session
python main.py chat
```

### Example: SQL review output

```
Reviewing: fct_orders

[HIGH] Missing dbt ref() macros — raw table names (orders, customers) bypass dbt's DAG.
  Fix: replace `from orders` with `from {{ ref('stg_orders') }}`

[MEDIUM] GROUP BY uses positional references (1,2,3...) — breaks silently if columns reorder.
  Fix: name each column explicitly in GROUP BY

[LOW] status filter uses != which excludes NULLs — may drop rows unintentionally.
  Fix: use `status not in ('cancelled') or status is null`
```

---

## Key API patterns used

```python
# Streaming (src/client.py)
with client.messages.stream(model=MODEL, ...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Structured output (src/doc_generator.py)
response = client.messages.parse(model=MODEL, ..., output_format=ModelDoc)
doc = response.parsed_output

# Multi-turn conversation (src/chat.py)
history.append({"role": "user", "content": user_input})
response = client.messages.create(model=MODEL, messages=history, ...)
history.append({"role": "assistant", "content": response_text})
```

---

## Stack

- **LLM**: Claude Opus 4.6 via [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- **CLI**: [Typer](https://typer.tiangolo.com/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Terminal UI**: [Rich](https://rich.readthedocs.io/)

---

## Resources

- [Anthropic API docs](https://platform.claude.com/docs)
- [Prompt engineering guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [dbt best practices](https://docs.getdbt.com/best-practices)
- [LangChain docs](https://python.langchain.com/docs/introduction/) — framework for chaining LLM calls
- [LlamaIndex docs](https://docs.llamaindex.ai/) — framework for RAG and document retrieval
