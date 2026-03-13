"""
Feature 2: dbt Documentation Generator

Demonstrates: few-shot prompt engineering + structured output (Pydantic).
"""

from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from src.prompts import DOC_GENERATOR_SYSTEM, FEW_SHOT_DOC_EXAMPLES

load_dotenv()

console = Console()
MODEL = "claude-opus-4-6"


# ── Structured output schema ──────────────────────────────────────────────────

class ColumnDoc(BaseModel):
    name: str
    description: str
    tests: list[str] = []


class ModelDoc(BaseModel):
    model_name: str
    description: str
    columns: list[ColumnDoc]
    yaml_output: str


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_docs(sql: str, model_name: str) -> ModelDoc:
    """
    Use few-shot examples + structured output to generate dbt schema.yml.

    The few-shot examples (defined in prompts.py) show Claude the exact
    format we expect before it sees the real SQL — a core prompt engineering
    technique.
    """
    console.print(
        Panel(
            f"[bold]Generating docs for:[/bold] {model_name}",
            style="green",
        )
    )

    client = anthropic.Anthropic()

    # Build messages: few-shot examples first, then the real request
    messages = [
        *FEW_SHOT_DOC_EXAMPLES,
        {
            "role": "user",
            "content": (
                f"Generate schema.yml documentation for this model:\n\n"
                f"```sql\n{sql}\n```\n"
                f"Model name: {model_name}"
            ),
        },
    ]

    # Use parse() for validated structured output
    response = client.messages.parse(
        model=MODEL,
        max_tokens=2048,
        system=DOC_GENERATOR_SYSTEM,
        messages=messages,
        output_format=ModelDoc,
    )

    doc: ModelDoc = response.parsed_output
    doc.model_name = model_name  # ensure it's set

    # Pretty-print the YAML
    console.print(Syntax(doc.yaml_output, "yaml", theme="monokai"))
    return doc
