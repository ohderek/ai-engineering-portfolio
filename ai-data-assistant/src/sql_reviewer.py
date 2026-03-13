"""
Feature 1: SQL Reviewer

Demonstrates: streaming + a well-crafted system prompt.
"""

from rich.console import Console
from rich.panel import Panel

from src.client import stream_response
from src.prompts import SQL_REVIEWER_SYSTEM

console = Console()


def review_sql(sql: str, model_name: str = "unknown") -> None:
    """Stream a code review for the given SQL."""
    console.print(
        Panel(
            f"[bold]Reviewing:[/bold] {model_name}",
            style="cyan",
        )
    )

    messages = [
        {
            "role": "user",
            "content": f"Please review this SQL model ({model_name}):\n\n```sql\n{sql}\n```",
        }
    ]

    stream_response(messages, system=SQL_REVIEWER_SYSTEM)
