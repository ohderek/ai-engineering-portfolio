"""
Feature 3: Interactive Data Engineering Chat

Demonstrates: multi-turn conversation management.
The API is stateless — we send the full history each turn.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.client import get_client, MODEL
from src.prompts import CHAT_SYSTEM

console = Console()


def run_chat() -> None:
    """REPL-style chat loop with conversation history."""
    console.print(
        Panel(
            "[bold cyan]AI Data Engineering Assistant[/bold cyan]\n"
            "Ask anything about SQL, dbt, Snowflake, Airflow, or Prefect.\n"
            "Type [bold]exit[/bold] to quit.",
            expand=False,
        )
    )

    client = get_client()
    history: list[dict] = []

    while True:
        user_input = console.input("\n[bold green]You:[/bold green] ").strip()
        if user_input.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye![/dim]")
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        console.print("\n[bold blue]Assistant:[/bold blue]")
        full_response = ""

        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=CHAT_SYSTEM,
            messages=history,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text

        print()
        history.append({"role": "assistant", "content": full_response})
